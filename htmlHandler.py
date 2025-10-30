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
    filewriter.write(_hlist, "finalfile.html")
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

def handlelist(listNode: WikiNode):
    _require_init()
    # unordered list
    if "*" in listNode.sarg:
        _write("<ul>")
        for item in listNode.children:
            if item.kind == NodeKind.LIST_ITEM:
                handlelist(item)  # if nested
            _write(f"<li>{item.sarg}</li>")
        _write("</ul>")
    # ordered list
    elif "#" in listNode.sarg:
        _write("<ol>")
        for item in listNode.children:
            if item.kind == NodeKind.LIST_ITEM:
                handlelist(item)
            _write(f"<li>{item.sarg}</li>")
        _write("</ol>")
