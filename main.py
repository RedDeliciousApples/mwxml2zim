from functools import partial
from typing import Any

from wikitextprocessor import Wtp, WikiNode, NodeKind, Page
from wikitextprocessor.dumpparser import process_dump
import re
import htmlHandler

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
wtp = Wtp()


# switch_dict = {
#    NodeKind.LEVEL2: html.level2(),
#    NodeKind.LEVEL3: action_for_case2,
#    NodeKind.LEVEL4: action_for_case3,
# }
# def switch_case(case):
#    action_function = switch_dict.get(case, lambda: "Default action")
#    return action_function()
def tohtml(tree):
    print("Got parse tree. Starting loop...")

    for i in tree:
        for child in i.children:

            print(str(child))
            #print("Loop begin")
            if (type(child) is str):
                print("Was str, continuing\n")
                #TODO should write str w/ filewriter instead of continuing

                continue
            if child.kind == NodeKind.LIST:
                print("A list was found")
                break
            if child.kind == NodeKind.LIST:
                print("List found, calling handleList...")
                htmlHandler.handlelist(child)
            elif child.kind == NodeKind.LINK:
                return
                #print("Link found")


        #print("\nThe " + str(child) + "was processed.\n")

#depth first search

def dfs(root):
    if root.kind != NodeKind.ROOT:
        print("not at root")
        return
    else:
        print("at root")
    print("dfs started")
    stack = [root]
    while stack:
        current_node = stack.pop()
        #print("Currently at node: " + str(current_node))
        if (type(current_node) is str):
            print("Was str, continuing\n")
            continue
        if (current_node.kind == NodeKind.ROOT):
            print("At root node!")


        if current_node.kind == NodeKind.LIST:
            print("A list was found")
            break
        if current_node.kind == NodeKind.LIST:
            print("List found, calling handleList...")
            #htmlHandler.handlelist(child)
        elif current_node.kind == NodeKind.LINK:
            return

        for child in reversed(current_node.children):
            stack.append(child)

stats = {"str": 0, "non_str": 0}

def traverse(node, depth=0):
    print(f'Processing node at depth {depth}: {node}')
    print(f'Type of node: {type(node)}')

    if not isinstance(node, WikiNode):
        #TODO Apparently, the parse tree can contain strings. Need to account for that
        if isinstance(node, str):
            stats["str"] += 1
        else:
            stats["non_str"] += 1
        print(f"Error: Expected WikiNode, got {type(node)}")
    return

    print(f'Node kind: {str(node.kind)}')
    
    for child in node.children:
        traverse(child, depth + 1)



def page_handler(page: Page, wtp: Wtp | None = None) -> Any:
    if page.model != "wikitext" or page.title.startswith("Template:"):
        print(page.title + " ignored")
        return ["fail on page " + page.title]
    #    tree = parser.parse(page.text, pre_expand=True)
    print("breakpoint page processed: " + page.title)
    # parse_tree.children returns alist of children, useful for iteration
    wtp.start_page(page.title)
    parse_tree = wtp.parse(page.body)
    print("Calling on type: " + str(type(parse_tree)))
    #print("\n\n\n text:\n\n\n" + wtp.expand(page.body))
    traverse(parse_tree, 0)
    print("Parsed " + page.title + ", sending to tohtml...")
    dfs(parse_tree)
    #tohtml(parse_tree)
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
    namespaces = {0, 10}
    process_dump(wtp, path, namespaces)
    for _ in map(
            partial(page_handler, wtp=wtp), wtp.get_all_pages([0], False)
    ):
        pass
    # we need all pages in Module: namespace, figuring out how to get these...
    # for e in search_tree:
    # print("iterated: " + str(len(e)))
    # print("\n\nhtml:\n\n" + parser.node_to_html(e))

    print("dump finish")
    print(f"String nodes: {stats['str']}, Non-string nodes: {stats['non_str']}")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # modulePath = "Wikipedia-popular-modules.xml"
    filePath = "appletrainboxtemplates.xml.bz2"
    # load_modules(modulePath)
    process_dump_internal(filePath)


def load_modules(path):
    namespaces = {828}
    print("Beegin module load...\n")
    list(wtp.process(path, page_handler, namespaces))



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
