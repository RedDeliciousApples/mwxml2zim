from platform import node

from wikitextprocessor import Wtp, WikiNode, NodeKind

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
parser = Wtp()


def page_handler(model, title, text) -> None:
    if model != "wikitext" or title.startswith("Template:"):
        return None
    tree = parser.parse(text, pre_expand=True)
    value = parser.node_to_wikitext(node)
    print(value)


def process_dump(file):
    parser.process("enwiktionary-20201201-pages-articles.xml.bz2", page_handler)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    file = open("Wikipedia-20230812015758.xml")
    process_dump(file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
