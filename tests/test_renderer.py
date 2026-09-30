"""Renderer tests: wikitext in, HTML out.

Assertions are deliberately loose about whitespace and paragraph tags so
they survive layout changes, but strict about content -- the old
renderer's failure mode was silently dropped or mangled text.

Run from the repository root:  python -m unittest
"""

import contextlib
import html
import io
import re
import unittest

from wikitextprocessor import Wtp

import htmlHandler

# One parser for every test; parse() needs a current page set first.
wtp = Wtp()


def render(text: str) -> str:
    """Render a wikitext fragment as a complete HTML document."""
    wtp.start_page("Test page")
    # The library prints parse warnings to stdout; keep test output clean.
    with contextlib.redirect_stdout(io.StringIO()):
        tree = wtp.parse(text)
    return htmlHandler.render_page("Test page", tree, wtp)


def visible(document: str) -> str:
    """Strip tags and collapse whitespace: roughly what a reader sees.

    Runs after unescaping, so deliberately escaped markup still counts
    as text, not as a tag."""
    body = document.partition("<body>")[2]
    without_tags = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


class DocumentShellTests(unittest.TestCase):
    def test_document_is_a_complete_html_page(self):
        document = render("Some text.")
        self.assertTrue(document.startswith("<!DOCTYPE html>"))
        self.assertIn("<meta charset=\"utf-8\" />", document)
        self.assertIn("<title>Test page</title>", document)
        self.assertIn("Some text.", document)


class StructureTests(unittest.TestCase):
    def test_heading_gets_its_own_tag_and_content_follows_it(self):
        document = render("Intro.\n==History==\nThe first trains ran.")
        self.assertIn("<h2>History</h2>", document)
        self.assertIn("The first trains ran.", visible(document))

    def test_section_content_is_not_swallowed_by_the_previous_section(self):
        document = render("==One==\nAlpha text.\n==Two==\nBeta text.")
        self.assertEqual(document.count("<h2"), 2)
        text = visible(document)
        self.assertIn("Alpha text.", text)
        self.assertIn("Beta text.", text)

    def test_heading_level_maps_to_html_level(self):
        document = render("===Subsection===\nBody.")
        self.assertIn("<h3>Subsection</h3>", document)

    def test_list_items_render_their_text_not_their_marker(self):
        document = render("* first item\n* second item")
        self.assertIn("<ul", document)
        self.assertIn("<li", document)
        text = visible(document)
        self.assertIn("first item", text)
        self.assertIn("second item", text)
        self.assertNotIn("*", text)  # the bullet is a tag, not content

    def test_numbered_list_uses_ol(self):
        document = render("# one\n# two")
        self.assertIn("<ol", document)


class EscapingTests(unittest.TestCase):
    def test_text_is_escaped(self):
        document = render("Tom & Jerry < 5")
        self.assertIn("&amp;", document)
        self.assertIn("&lt;", document)
        self.assertIn("Tom & Jerry < 5", visible(document))


class InlineMarkupTests(unittest.TestCase):
    def test_bold_and_italic(self):
        document = render("'''bold''' and ''italic''")
        self.assertIn("<b>bold</b>", document)
        self.assertIn("<i>italic</i>", document)

    def test_links_render_display_text_without_a_url(self):
        # No link scheme is chosen yet (deferred); links stay plain text.
        document = render("See [[wagonway|wagon ways]] and [[railway]].")
        text = visible(document)
        self.assertIn("wagon ways", text)
        self.assertIn("railway", text)
        self.assertNotIn("<a ", document)

    def test_ref_renders_inline_and_empty_stubs_are_dropped(self):
        document = render("<ref>Some source, 1920.</ref>")
        self.assertIn("<span class=\"reference\"", document)
        self.assertIn("Some source, 1920.", visible(document))

        stub_only = render("Text.<ref name=\"x\"/>")
        self.assertNotIn("<span class=\"reference\"", stub_only)


class TemplateTests(unittest.TestCase):
    def test_unknown_template_falls_back_to_its_argument_text(self):
        # cite web is not in the (empty) template database, so the
        # fallback path renders argument values without parameter labels.
        document = render("{{cite web|title=The Box}}")
        text = visible(document)
        self.assertIn("The Box", text)
        self.assertNotIn("title=", text)


class IndexTests(unittest.TestCase):
    def test_index_links_every_entry_with_escaped_titles(self):
        document = htmlHandler.render_index(
            [("Apple", "Apple.html"), ("A&B", "A&B.html")]
        )
        self.assertIn('<a href="Apple.html">Apple</a>', document)
        self.assertIn('<li><a href="A&amp;B.html">A&amp;B</a></li>', document)
        self.assertNotIn("A&B", document)  # raw ampersand must be escaped


if __name__ == "__main__":
    unittest.main()
