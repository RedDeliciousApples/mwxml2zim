import filewriter


def level2(text):
    content = "<h2> " + text + "</h2> <br />"
    filewriter.write("my_page.html", content)

def level3(text):
    content = "<h3> " + text + "</h3> <br />"
    filewriter.write("my_page.html", content)