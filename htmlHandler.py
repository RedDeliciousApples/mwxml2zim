from typing import Optional
from wikitextprocessor import WikiNode, NodeKind
import filewriter

_hlist: Optional[list] = None  # module-level shared state

def begin():
    #make sure to call this 1st
    global _hlist
    _hlist = filewriter.init()
    return _hlist

def _require_init():
    if _hlist is None:
        raise RuntimeError("Call begin() before using writer functions. You did not call begin(), which is why you are getting this error.")

def _write(content: str):
    _require_init()
    filewriter.write(content, _hlist)
def end():
    filewriter.writeClose(_hlist, "finalfile.html")
def level2(text: str):
    _write(f"<h2>{text}</h2><br />")

def level3(text: str):
    _write(f"<h3>{text}</h3><br />")

def level4(text: str):
    _write(f"<h4>{text}</h4><br />")

def level5(text: str):
    _write(f"<h5>{text}</h5><br />")

def level6(text: str):
    _write(f"<h6>{text}</h6><br />")

def italic(text: str):
    _write(f"<i>{text}</i>")

def bold(text: str):
    _write(f"<b>{text}</b>")

def hline():
    _write("<hr>")

def handlelist(list_node: WikiNode):
    _require_init()

    if list_node.sarg.endswith("*"):
        tag = "ul"
    else:
        tag = "ol"

    _write(f"<{tag}>")

    for item in list_node.children:
        if isinstance(item, str):
            _write(item)
            continue

        if item.kind != NodeKind.LIST_ITEM:
            continue

        _write("<li>")

        for child in item.children:
            if isinstance(child, str):
                _write(child)
            elif child.kind == NodeKind.LIST:
                handlelist(child)

        _write("</li>")

    _write(f"</{tag}>")