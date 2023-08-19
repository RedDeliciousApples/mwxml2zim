from wikitextprocessor import Wtp, WikiNode, NodeKind, Page

import re
import html

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
parser = Wtp()


def removeTemplate(input_string: str) -> str:
    # Define a regular expression pattern to match text between curly braces
    pattern = r'\{[^}]*\}'

    # Use re.sub() to replace the matched pattern with an empty string
    result = re.sub(pattern, '', input_string)

    return result


def remove_closing_curly_braces(input_string):
    # Define a regular expression pattern to match closing curly braces
    pattern = r'\}'

    # Use re.sub() to replace the matched pattern with an empty string
    result = re.sub(pattern, '', input_string)

    return result

#switch_dict = {
#    NodeKind.LEVEL2: html.level2(),
#    NodeKind.LEVEL3: action_for_case2,
#    NodeKind.LEVEL4: action_for_case3,
#}
#def switch_case(case):
#    action_function = switch_dict.get(case, lambda: "Default action")
#    return action_function()
def tohtml(tree):
    for child in tree.children:
        print(child.title())
        if NodeKind.LEVEL2:
            html.level2(child.args)




def page_handler(page: Page) -> [1, 2, 3]:
    if page.model != "wikitext" or page.title.startswith("Template:"):
        print(page.title + " ignored")
        return ["fail on page " + page.title]
    #    tree = parser.parse(page.text, pre_expand=True)
    print("breakpoint page processed: " + page.title)
    # parse_tree.children returns alist of children, useful for iteration
    parse_tree = parser.parse(page.body)
    tohtml(parse_tree)
    #for i in parse_tree.children:
    #    nodeKind = i.kind
        # ??? python has no swicth stements ???
    #print(parse_tree.children[24])
    # for e in parse_tree.children:
    #    print(e)

    ftext = removeTemplate(page.body)
    text = remove_closing_curly_braces(ftext)
    # TODO big improvements needed for node_to_html, maybe use mwparserfromhell?
    # filewriter.write("my_file-{}.html".format(page.title), parsed_page.get("html"))
    # print("page text: " + text)



def process_dump(path):
    namespaces = {0, 10}
    search_tree = list(parser.process(path, page_handler, namespaces))
    # we need all pages in Module: namespace, figuring out how to get these...
    # for e in search_tree:
    # print("iterated: " + str(len(e)))
    # print("\n\nhtml:\n\n" + parser.node_to_html(e))

    print("dump finish")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # modulePath = "Wikipedia-popular-modules.xml"
    filePath = "appletrainboxtemplates.xml"
    # load_modules(modulePath)
    process_dump(filePath)


def load_modules(path):
    namespaces = {828}
    print("Beegin module load...\n")
    list(parser.process(path, page_handler, namespaces))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
