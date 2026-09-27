import logging

logger = logging.getLogger(__name__)


def write(content,list) -> None:
    list.append(content)
def init() -> list:
    #starts a list with open html template
    htmlList = []
    htmlList.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blank HTML Template</title></head>
            <body>
        """)
    return htmlList

def writeClose(writelist, path):
    writelist.append("""
        </body>""")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(writelist))
    except OSError:
        logger.exception("An error occurred and the file could not be written: %s", path)
    else:
        logger.info("File written successfully: %s", path)


