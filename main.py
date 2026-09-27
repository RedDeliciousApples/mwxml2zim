import argparse
from functools import partial
import logging
import sys
from typing import Any

# Parse trees regularly contain characters (e.g. ², ₂) that the Windows
# console encoding (cp1252) cannot encode; make stdout/stderr UTF-8 so
# debug printing does not crash mid-dump.
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from wikitextprocessor import Wtp, WikiNode, NodeKind, Page
from wikitextprocessor.dumpparser import process_dump
import re
import htmlHandler

logger = logging.getLogger(__name__)

DEFAULT_DUMP = "appletrainboxtemplates.xml.bz2"

wtp = Wtp()
thelist = htmlHandler.begin()

# switch_dict = {
#    NodeKind.LEVEL2: html.level2(),
#    NodeKind.LEVEL3: action_for_case2,
#    NodeKind.LEVEL4: action_for_case3,
# }
# def switch_case(case):
#    action_function = switch_dict.get(case, lambda: "Default action")
#    return action_function()
DISPATCH = {
    NodeKind.LIST: htmlHandler.handlelist,
    NodeKind.LEVEL2: lambda n: htmlHandler.level2(n.sarg),
    NodeKind.LEVEL3: lambda n: htmlHandler.level3(n.sarg),
    NodeKind.LEVEL4: lambda n: htmlHandler.level4(n.sarg),
}
def tohtml(tree):
    logger.debug("Got parse tree. Starting loop...")

    for child in tree.children:
        logger.debug("%s", child)
        if (type(child) is str):
            logger.debug("Was str, writing...")
            #cast to str just in case
            htmlHandler._write(str(child))

            continue
        handler = DISPATCH.get(child.kind)
        if handler:
            handler(child)
            continue

#depth first search

def dfs(root):
    if root.kind != NodeKind.ROOT:
        logger.debug("not at root")
        return
    else:
        logger.debug("at root")
    logger.debug("dfs started")
    stack = [root]
    while stack:
        current_node = stack.pop()
        if (type(current_node) is str):
            logger.debug("Was str, continuing")
            continue
        if (current_node.kind == NodeKind.ROOT):
            logger.debug("At root node!")


        if current_node.kind == NodeKind.LIST:
            logger.debug("A list was found")
            logger.debug("List found, calling handleList...")
            #htmlHandler.handlelist(child)
            break

        elif current_node.kind == NodeKind.LINK:
            logger.debug("found link from the legend of zelda")
            return

        for child in reversed(current_node.children):
            stack.append(child)

stats = {"str": 0, "non_str": 0}

def traverse(node, depth=0):
    logger.debug("Processing node at depth %s: %s", depth, node)
    logger.debug("Type of node: %s", type(node))


    # Strings are normal in parse trees (plain wikitext text), not an error
    if isinstance(node, str):
        stats["str"] += 1
        return
    stats["non_str"] += 1


    if not isinstance(node, WikiNode):
        logger.error("Expected WikiNode, got %s", type(node))
        return




    logger.debug("Node kind: %s", node.kind)

    for child in node.children:
        traverse(child, depth + 1)



def page_handler(page: Page, wtp: Wtp | None = None) -> Any:
    if page.model != "wikitext" or page.title.startswith("Template:"):
        logger.debug("%s ignored", page.title)
        return ["fail on page " + page.title]
    #    tree = parser.parse(page.text, pre_expand=True)
    logger.info("Processing page: %s", page.title)
    # parse_tree.children returns alist of children, useful for iteration
    wtp.start_page(page.title)
    parse_tree = wtp.parse(page.body)
    logger.debug("Calling on type: %s", type(parse_tree))
    traverse(parse_tree, 0)
    logger.debug("Parsed %s, sending to tohtml...", page.title)
    dfs(parse_tree)
    tohtml(parse_tree)
    # for i in parse_tree.children:
    #    nodeKind = i.kind
    # ??? python has no swicth stements ???
    # print(parse_tree.children[24])
    # for e in parse_tree.children:
    #    print(e)
    #TODO implement
        #ftext = removeTemplate(page.body)
        #text = remove_closing_curly_braces(ftext)
    # filewriter.write("my_file-{}.html".format(page.title), parsed_page.get("html"))
    # print("page text: " + text)


def process_dump_internal(path):
    logger.info("Reading dump: %s", path)
    namespaces = {0, 10}
    process_dump(wtp, path, namespaces)
    for _ in map(
            partial(page_handler, wtp=wtp), wtp.get_all_pages([0], False)
    ):
        pass
    # we need all pages in Module: namespace, figuring out how to get these...

    logger.info("Dump finished")
    logger.info("String nodes: %s, Non-string nodes: %s", stats["str"], stats["non_str"])
    htmlHandler.end()


def load_modules(path):
    namespaces = {828}
    logger.info("Beginning module load...")
    list(wtp.process(path, page_handler, namespaces))


def _configure_logging(verbose: bool = False, log_file: str | None = None) -> None:
    """Console shows INFO progress only; -v/--verbose adds the per-node
    DEBUG detail. --log-file always captures DEBUG so the spam stays
    available without flooding the terminal.

    Root is set to DEBUG and each handler filters its own level --
    basicConfig(level=..., handlers=...) would ignore the level."""
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(logging.Formatter("%(levelname)-7s %(name)s: %(message)s"))

    handlers: list[logging.Handler] = [console]
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
        )
        handlers.append(file_handler)

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    root.setLevel(logging.DEBUG)
    for handler in handlers:
        root.addHandler(handler)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a MediaWiki XML dump to HTML (ZIM output not implemented yet)."
    )
    parser.add_argument(
        "dump", nargs="?", default=DEFAULT_DUMP,
        help="path to a <project>-<date>-pages-articles.xml.bz2 dump (default: %(default)s)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="log per-node parse-tree detail to the console",
    )
    parser.add_argument(
        "--log-file", metavar="PATH",
        help="also write DEBUG-level logs to PATH",
    )
    args = parser.parse_args()

    _configure_logging(args.verbose, args.log_file)
    process_dump_internal(args.dump)


if __name__ == '__main__':
    main()

