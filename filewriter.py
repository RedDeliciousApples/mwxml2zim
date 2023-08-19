def write(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print("File written successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
def init() -> list:
    #starts a list with open html template
    htmlList = []
    htmlList.insert("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blank HTML Template</title>
        </head>
        <body>""")
    return htmlList
