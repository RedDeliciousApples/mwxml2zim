def write(content,list) -> None:
    list.append(content)
def init() -> list:
    html_list = []
    html_list.append("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Wikipedia article</title>
        </head>
        <body>
        """)
    return html_list


def writeClose(write_list, path):
    write_list.append("""
        </body>
        </html>
        """)

    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write("\n".join(write_list))
        print(f"File written successfully: {path}")
    except OSError as error:
        print(f"An error occurred and the file could not be written: {error}")


