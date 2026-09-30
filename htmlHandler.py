"""Renders a wikitextprocessor parse tree as HTML.

The entry point is render_page(title, tree, wtp), which returns a complete
HTML document for one wiki page.  Everything else here is the walk itself:

* _render() accepts one parse-tree value: a plain string, a nested list
  (node arguments are lists of lists), or a WikiNode.
* WikiNodes are handed to the handler listed for their NodeKind in HANDLERS.
* A node kind without a handler falls back to rendering its children, so no
  text is ever silently dropped.
"""

import contextlib
import html
import io
import logging
import re

from wikitextprocessor import NodeKind, WikiNode

logger = logging.getLogger(__name__)

# The whole document shell for one page.  str.format() is used, which is why
# the CSS braces below are doubled.
DOCUMENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>{title}</title>
    <style>
        /* Stand-in for the proper <sup> citation markers, see RefTagsNotes.txt */
        span.reference {{ font-size: 0.85em; color: #555; }}
    </style>
</head>
<body>
{body}
</body>
</html>
"""

HEADING_TAGS = {
    NodeKind.LEVEL1: "h1",
    NodeKind.LEVEL2: "h2",
    NodeKind.LEVEL3: "h3",
    NodeKind.LEVEL4: "h4",
    NodeKind.LEVEL5: "h5",
    NodeKind.LEVEL6: "h6",
}

# HTML tags MediaWiki writes without content of their own
VOID_HTML_TAGS = {"br", "hr"}

# Container tags whose wikitext content is a list of files or source code;
# without the files themselves there is nothing worth showing
DROPPED_HTML_TAGS = {"gallery", "imagemap", "timeline"}

# [[File:...]] arguments that only place the image, not caption text
MEDIA_LAYOUT_ARGS = {
    "thumb", "thumbnail", "frame", "frameless", "right", "left", "center",
    "none", "upright",
}

# [[File:...]] arguments that are technical settings rather than anything a
# reader should see ("alt=...", "width=...")
MEDIA_TECHNICAL_ARGS = {
    "alt", "link", "page", "class", "style", "width", "height", "border",
    "thumbnailtime", "thumbtime",
}

# Anything that does not look like a normal HTML attribute name (an
# attribute name is what could carry event handlers) is not passed through
ATTRIBUTE_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")


def render_page(title: str, tree: WikiNode, wtp=None) -> str:
    """Render one parsed page and return a complete HTML document.

    ``tree`` is the ROOT node returned by wikitextprocessor's parse().
    ``wtp`` is the Wtp instance used to re-parse the wikitext that sits
    inside template and link arguments (pass None to keep that text as-is).
    """
    return Renderer(title, wtp).render_document(tree)


def _plain_text(value) -> str:
    """Flatten a parse-tree value (string, nested list or WikiNode) to text."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_plain_text(item) for item in value)
    if isinstance(value, WikiNode):
        return "".join(_plain_text(child) for child in value.children)
    return ""


def _list_tag(prefix: str) -> str:
    """Map a wikitext list prefix ("*", "#", ";", ":") to an HTML tag."""
    if "*" in prefix:
        return "ul"
    if "#" in prefix:
        return "ol"
    return "dl"  # ";" and ":" build definition lists


def _is_media_argument(text: str) -> bool:
    """True for a [[File:...]] argument that is not caption text: the ones
    that only place the image (thumb, left, 200px) and the technical ones
    (alt=..., link=..., width=...)."""
    if text.endswith("px"):  # "200px", "640x480px"
        return True
    if "=" in text:
        label, _separator, _value = text.partition("=")
        return label.strip().lower() in MEDIA_TECHNICAL_ARGS
    return text.lower() in MEDIA_LAYOUT_ARGS


class Renderer:
    """Renders a single page.  Create one, call render_document(), discard it."""

    def __init__(self, title: str, wtp=None) -> None:
        self.title = title
        self.wtp = wtp
        self.parts: list[str] = []

    def render_document(self, tree: WikiNode) -> str:
        self._render_children(tree)
        return DOCUMENT.format(
            title=html.escape(self.title),
            body="".join(self.parts),
        )

    # ------------------------------------------------------------- plumbing

    def _write(self, fragment: str) -> None:
        self.parts.append(fragment)

    def _render_children(self, node: WikiNode) -> None:
        for child in node.children:
            self._render(child)

    def _render(self, value) -> None:
        """Render one parse-tree value: text, a nested list of values, or a
        WikiNode (dispatched to its handler below)."""
        if isinstance(value, str):
            self._write(html.escape(value))
        elif isinstance(value, list):
            for item in value:
                self._render(item)
        elif isinstance(value, WikiNode):
            self._render_node(value)
        else:
            logger.debug("Ignoring %r, not a parse-tree value", value)

    def _render_node(self, node: WikiNode) -> None:
        handler = HANDLERS.get(node.kind)
        if handler is None:
            logger.debug("No handler for %s, rendering its children",
                         node.kind.name)
            self._render_children(node)
            return
        handler(self, node)

    def _render_fragment(self, text: str) -> None:
        """Render a piece of wikitext that is still unparsed.

        Template and link arguments are handed to us as raw wikitext
        (''italics'', <small>, <ref>, * lists, nested {{templates}}), so it
        is parsed here first: that turns the markup into real nodes instead
        of letting it show up as escaped literal text.
        """
        if self.wtp is None:
            self._write(html.escape(text))
            return

        # MediaWiki trims template arguments before it uses them; without
        # this, a value like " Apple" (the space in "| name = Apple") would
        # come back as a spurious <pre> block.
        text = text.strip()
        if not text:
            return

        # A single-line fragment that starts with "*", "#", ";" or ":" would
        # be parsed as a list simply because it starts a line here, while in
        # the article it is usually mid-sentence (a reconstruction such as
        # "*aplaz" in {{lang|gem-x-proto|*aplaz}}).  Keep that literal.
        # Multi-line fragments keep their lists: there the markers really
        # are at the start of a line.
        if "\n" not in text and text[:1] in "*#;:":
            self._write(html.escape(text))
            return

        # wikitextprocessor prints its parse warnings straight to stdout and
        # has no flag to turn that off.  Capture them while parsing a
        # fragment (a fragment is a poor context for them anyway) and keep
        # them as DEBUG lines instead.
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            tree = self.wtp.parse(text)
        for line in captured.getvalue().splitlines():
            if line.strip():
                logger.debug("parse note: %s", line)

        self._render_children(tree)

    def _render_wikitext_items(self, items) -> None:
        """Render a list of raw wikitext strings and already-parsed nodes,
        which is what template and link arguments are made of."""
        if not isinstance(items, list):
            items = [items]
        for item in items:
            if isinstance(item, str):
                self._render_fragment(item)
            else:
                self._render(item)

    def _wrap(self, tag: str, node: WikiNode) -> None:
        """Write <tag>, the node's children, then </tag>."""
        self._write(f"<{tag}{self._attributes(node.attrs)}>")
        self._render_children(node)
        self._write(f"</{tag}>")

    def _attributes(self, attrs: dict) -> str:
        """Turn a node's HTML attributes into ' class="wikitable" ...'.

        Values are quoted and escaped so they cannot break out of the tag,
        and attribute names that do not look like plain HTML attribute names
        are dropped rather than passed through."""
        written = ""
        for name, value in attrs.items():
            if not ATTRIBUTE_NAME.fullmatch(str(name)):
                logger.debug("Dropping suspicious attribute %r", name)
                continue
            written += f' {name}="{html.escape(str(value), quote=True)}"'
        return written

    # ------------------------------------------------------------- headings

    def _heading(self, node: WikiNode) -> None:
        # The section title lives in node.largs.  node.sarg only holds the
        # "=" marker (and is empty for headings), which is why reading sarg
        # used to produce empty <h2></h2> tags.  The section's content is
        # in the node's children and follows the heading.
        tag = HEADING_TAGS[node.kind]
        self._write(f"<{tag}>")
        self._render(node.largs)
        self._write(f"</{tag}>\n")
        self._render_children(node)

    def _horizontal_rule(self, node: WikiNode) -> None:
        self._write("<hr />\n")

    def _italic(self, node: WikiNode) -> None:
        self._wrap("i", node)

    def _bold(self, node: WikiNode) -> None:
        self._wrap("b", node)

    # ---------------------------------------------------------------- lists

    def _list(self, node: WikiNode) -> None:
        """LIST nodes hold their LIST_ITEM children.  A nested list is a
        child of its own item, so it ends up inside the right <li>/<dd>."""
        tag = _list_tag(str(node.sarg))
        self._write(f"<{tag}>\n")
        self._render_children(node)
        self._write(f"</{tag}>\n")

    def _list_item(self, node: WikiNode) -> None:
        if node.sarg.startswith(";"):
            tag = "dt"
        elif node.sarg.startswith(":"):
            tag = "dd"
        else:
            tag = "li"

        self._write(f"<{tag}>")
        self._render_children(node)
        self._write(f"</{tag}>")

        if node.definition:
            # A ";" definition-list item keeps its definition in a separate
            # field instead of in its children; it becomes the <dd>.
            self._write("<dd>")
            self._render(node.definition)
            self._write("</dd>")

    # -------------------------------------------------- links and external

    def _link(self, node: WikiNode) -> None:
        """[[Target|Text]] and friends.

        Links are deliberately plain text for now: how articles will be
        addressed inside the ZIM file gets decided later, so for the moment
        only the words survive.  Category links vanish completely (their
        markup is metadata, not prose) while file links keep their caption.
        """
        if not node.largs:
            return
        target = _plain_text(node.largs[0])
        namespace = target.partition(":")[0].lower()

        if namespace == "category":
            return

        if namespace in ("file", "image"):
            self._render_captions(node.largs[1:])
        else:
            # No pipe: the target doubles as the display text
            display = node.largs[1] if len(node.largs) > 1 else node.largs[0]
            self._render_wikitext_items(display)

        # "[[link]]s" keeps its trailing "s" in the node's children
        self._render_children(node)

    def _render_captions(self, arguments) -> None:
        """Write the caption of a [[File:...]] link, skipping the arguments
        that only place the image or configure it (thumb, left, alt=...)."""
        for argument in arguments:
            text = _plain_text(argument).strip()
            if not text or _is_media_argument(text):
                continue
            self._render_wikitext_items(argument)
            self._write(" ")

    def _url(self, node: WikiNode) -> None:
        """[https://example Text] -- also plain text, for the same reason.

        Deliberately not passed through _render_fragment(): the parser turns
        a bare "https://..." right back into a URL node, so re-parsing a
        display text that happens to be a URL would recurse forever.
        """
        if not node.largs:
            return
        # The display text when given, the URL itself otherwise
        display = node.largs[1] if len(node.largs) > 1 else node.largs[0]
        self._write(html.escape(_plain_text(display)))

    # --------------------------------------- templates and parser functions

    def _template_fallback(self, node: WikiNode) -> None:
        """Fallback for {{name|args}}, {{#parserfunction|args}} and
        {{{argument|default}}}.

        Templates are not expanded (only the ones that change the page's
        structure are, at parse time), so their argument text is written
        instead of dropping the node.  This is what keeps citation text
        such as {{cite web|title=...}} visible in the article.
        """
        for index, argument in enumerate(node.largs[1:]):
            if index:
                self._write(" ")
            self._render_argument(argument)

    def _render_argument(self, argument) -> None:
        """Render one template argument.

        Named arguments start with "label="; the label is a parameter name,
        not prose, so it is dropped ({{cite web|title=Apple}} renders as
        "Apple", not "title=Apple")."""
        items = argument if isinstance(argument, list) else [argument]
        if items and isinstance(items[0], str) and "=" in items[0]:
            _label, _separator, value = items[0].partition("=")
            items = [value] + items[1:]
        self._render_wikitext_items(items)

    def _magic_word(self, node: WikiNode) -> None:
        """__TOC__, __NOTOC__ and friends produce nothing worth rendering."""
        logger.debug("Skipping magic word %s", node.sarg)

    # --------------------------------------------------------------- tables

    def _table(self, node: WikiNode) -> None:
        self._wrap("table", node)
        self._write("\n")

    def _table_caption(self, node: WikiNode) -> None:
        self._wrap("caption", node)

    def _table_row(self, node: WikiNode) -> None:
        self._wrap("tr", node)
        self._write("\n")

    def _table_header_cell(self, node: WikiNode) -> None:
        self._wrap("th", node)

    def _table_cell(self, node: WikiNode) -> None:
        self._wrap("td", node)

    # -------------------------------------------------------- preformatted

    def _preformatted(self, node: WikiNode) -> None:
        """Space-indented lines (markup still interpreted) and <pre> blocks."""
        self._wrap("pre", node)

    # ------------------------------------------------------- raw HTML tags

    def _html_tag(self, node: WikiNode) -> None:
        """Raw HTML from the wikitext: <ref>, <div>, <br/>, <gallery>, ..."""
        tag = str(node.sarg).lower()
        attributes = self._attributes(node.attrs)

        if tag == "ref":
            # Citations stay inline as plain text for now; the real <sup>
            # marker plus a reference list is a later milestone
            # (RefTagsNotes.txt).  <ref name="x"/> stubs have no children.
            if node.children:
                self._write(f'<span class="reference"{attributes}>')
                self._render_children(node)
                self._write("</span>")
            return

        if tag in DROPPED_HTML_TAGS:
            logger.debug("Dropping <%s> content", tag)
            return

        if tag in VOID_HTML_TAGS:
            self._write(f"<{tag}{attributes} />")
            return

        if not node.children:
            # An empty unknown tag left open could swallow the rest of the
            # page, and it has no content worth showing either.
            logger.debug("Dropping empty <%s> tag", tag)
            return

        self._write(f"<{tag}{attributes}>")
        self._render_children(node)
        self._write(f"</{tag}>")


# Which function renders which parse node.  Registered after the class so the
# handlers can be written as ordinary methods; _render_node() calls them as
# handler(self, node).  ROOT is not listed because render_document() walks
# its children directly, and a node kind without a handler (if a future
# library version adds one) falls back to rendering its children.
HANDLERS = {
    NodeKind.LEVEL1: Renderer._heading,
    NodeKind.LEVEL2: Renderer._heading,
    NodeKind.LEVEL3: Renderer._heading,
    NodeKind.LEVEL4: Renderer._heading,
    NodeKind.LEVEL5: Renderer._heading,
    NodeKind.LEVEL6: Renderer._heading,
    NodeKind.ITALIC: Renderer._italic,
    NodeKind.BOLD: Renderer._bold,
    NodeKind.HLINE: Renderer._horizontal_rule,
    NodeKind.LIST: Renderer._list,
    NodeKind.LIST_ITEM: Renderer._list_item,
    NodeKind.PREFORMATTED: Renderer._preformatted,
    NodeKind.PRE: Renderer._preformatted,
    NodeKind.LINK: Renderer._link,
    NodeKind.URL: Renderer._url,
    NodeKind.TEMPLATE: Renderer._template_fallback,
    NodeKind.PARSER_FN: Renderer._template_fallback,
    NodeKind.TEMPLATE_ARG: Renderer._template_fallback,
    NodeKind.MAGIC_WORD: Renderer._magic_word,
    NodeKind.TABLE: Renderer._table,
    NodeKind.TABLE_CAPTION: Renderer._table_caption,
    NodeKind.TABLE_ROW: Renderer._table_row,
    NodeKind.TABLE_HEADER_CELL: Renderer._table_header_cell,
    NodeKind.TABLE_CELL: Renderer._table_cell,
    NodeKind.HTML: Renderer._html_tag,
}
