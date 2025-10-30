def write(content, list):
    list.add(content)
    return list
def init() -> list:
    #starts a list with open html template
    htmlList = []
    htmlList.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blank HTML Template</title>
        """)
    return htmlList

def writeClose(list, path):
    list.append("""</head>
        <body>""")
    for i in list:
        try:
            with open(path, 'w') as file:
                file.write(i)
            print("File written successfully.")
        except Exception as e:
            print(f"An error occurred and the file could not be written: {e}")
    file.close()


