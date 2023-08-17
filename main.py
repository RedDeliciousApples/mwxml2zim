from wikitextprocessor import Wtp, WikiNode, NodeKind, Page

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
parser = Wtp()


def page_handler(page: Page) -> [1,2,3]:
    if page.model != "wikitext" or page.title.startswith("Template:"):
        print(page.title)
        return ["fail"]
    #    tree = parser.parse(page.text, pre_expand=True)
    if page.title.startswith("A"):
        print(page.title)
    print("breakpoint page processed")


def process_dump(path):
    # TODO /tmp doesnt exist on windows, use different folder
    namespaces = {100, }
    print(list(parser.process(path, page_handler, namespaces)))
    print("breakpoint2")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    filePath = "Wikipedia-20230812015758.xml"
    process_dump(filePath)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
