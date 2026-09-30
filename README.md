# MediaWiki dump → static HTML (proof of concept)

Renders articles from a MediaWiki XML dump (the kind Wikipedia publishes) as
static HTML: one file per page, plus an index linking them together. No ZIM
packaging; see [Limitations](#limitations).

Copyright © 2025 Christian Saliba

## How it works

1. **Phase 1** — `wikitextprocessor` extracts the dump into a SQLite cache
2. Each article's wikitext is parsed with `pre_expand=True`, so the templates
   that change a page's structure (tables, lists, infoboxes) are expanded
   before the traversal begins.
3. `htmlHandler.Renderer` traverses the parse tree and writes one document per
   page; `out/index.html` links them together.

## Quick start

```bash
pip install -r requirements.txt
python main.py
python main.py my-dump.xml.bz2 -o out/
```

Options: `-v` for verbose, `--log-file PATH` captures the full
DEBUG log. Tested with Python 3.13; the dump must be `.bz2`.

## Demo

* **Input:** `demo/input.xml.bz2` — a two-page synthetic dump (843 bytes)
* **Output:** `demo/output/` — HTML generated from the fixture
* Regenerate: `python main.py demo/input.xml.bz2 -o demo/output`
* Closer to production data: `appletrainboxtemplates.xml.bz2` holds three real
  articles plus ~160 of their templates.

## Tests

```bash
python -m unittest        # from the repository root
```

## Repository layout

| Path | Role |
| --- | --- |
| `main.py` | CLI, dump pipeline, index generation |
| `htmlHandler.py` | parse tree to HTML document |
| `filewriter.py` | file naming and writing pages |
| `tests/` | renderer tests |
| `demo/` | miniature input dump and some output |

## Limitations

* **No ZIM output.** The project used to aim at `.zim` files; it is now a
  static-HTML proof of concept and packaging is out of scope.
* **No images.** `[[File:...]]` captions stay as text only.
* **Links are plain text.** Article-to-article URLs are not generated.
* **Templates are only partly expanded.** For example, `{{lang|ang-Latn|Äppel}}` becomes "ang-Latn Äppel".
* **Scribunto (Lua) templates cannot run** unless `Module:` pages are loaded.
* **HTML styling is minimal.** There is no project stylesheet.

## Project status

This is a completed proof of concept; no active development is planned. Forks
are welcome under the license below.

## License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
