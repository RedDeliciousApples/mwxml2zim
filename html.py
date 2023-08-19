import filewriter


def level2(text):
    content = "<h2> " + text + "</h2>"
    filewriter.write("my_page.html", content)