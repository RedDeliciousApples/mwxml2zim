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
