import random

from wikitextprocessor import Wtp, WikiNode, NodeKind, Page

import filewriter

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
parser = Wtp()


def page_handler(page: Page) -> [1, 2, 3]:
    if page.model != "wikitext" or page.title.startswith("Template:"):
        print(page.title + " ignored")
        return ["fail on page " + page.title]
    #    tree = parser.parse(page.text, pre_expand=True)
    print("breakpoint page processed: " + page.title)
    node = parser.parse(str(page.body), True, True)
    #TODO big improvements needed for node_to_html, maybe use mwparserfromhell?
    filewriter.write("my_file-{}.html".format(page.title) , parser.node_to_html(node))
    print("page text: " + str(node))


def process_dump(path):
    namespaces = {0, 10}
    search_tree = list(parser.process(path, page_handler, namespaces))
    # we need all pages in Module: namespace, figuring out how to get these...
    #for e in search_tree:
       # print("iterated: " + str(len(e)))
        #print("\n\nhtml:\n\n" + parser.node_to_html(e))

    print("dump finish")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    modulePath = "Wikipedia-popular-modules.xml"
    filePath = "appletrainboxtemplates.xml"
    load_modules(modulePath)i
    process_dump(filePath)

def load_modules(path):
    namespaces = {828}
    print("Beegin module load...\n")
    list(parser.process(path, page_handler, namespaces))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
