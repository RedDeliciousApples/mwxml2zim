from wikitextprocessor import WikiNode, NodeKind

import filewriter

list = filewriter.init()


def level2(text):
    content = "<h2> " + text + "</h2> <br />"
    filewriter.write(content, list)


def level3(text):
    content = "<h3> " + text + "</h3> <br />"
    filewriter.write(content, list)


def level4(text):
    content = "<h4> " + text + "</h4> <br />"
    filewriter.write(content, list)


def level5(text):
    content = "<h5> " + text + "</h5> <br />"
    filewriter.write(content, list)


def level6(text):
    content = "<h6> " + text + "</h6> <br />"
    filewriter.write(content, list)

def italic(text):
    content = "<i> " + text + "</i>"
    filewriter.write(content, list)

def bold(text):
    content = "<b>" + text + "</b>"
    filewriter.write(content, list)

def hline():
    content = "<hr>"
    filewriter.write(content, list)

def handlelist(listNode: WikiNode):
    level = len(listNode.sarg)
    #unordered list
    if (listNode.sarg.__contains__("*")):
        filewriter.write("<ul> ", list)
        for item in listNode.children:
            #handle multilevel lists
            if item.kind == NodeKind.LIST_ITEM:
                handlelist(item)
            content = "<li> " + item.sarg + "</li>"
            filewriter.write(content, list)
        print(filewriter.write("</ul>", list))

    #ordered list
    elif (listNode.sarg.__contains__("#")):
        filewriter.write("<ol> ", list)
        for item in listNode.children:
            # handle multilevel lists
            if item.kind == NodeKind.LIST_ITEM:
                handlelist(item)
            content = "<li> " + item.sarg + "</li>"
            filewriter.write(content, list)
        print(filewriter.write("</ol>", list))

    print("placeholder")