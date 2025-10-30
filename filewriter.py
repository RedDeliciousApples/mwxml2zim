def write(content, list) -> None:
    list.append(content)
def init() -> list:
    #starts a list with open html template
    htmlList = []
    htmlList.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blank HTML Template</title>
            <body>
        """)
    return htmlList

def writeClose(list, path):
    list.append("""</head>
        </body>""")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(list))
        print(f"File written successfully: {path}")
    except OSError as e:
        print(f"An error occurred and the file could not be written: {e}")


