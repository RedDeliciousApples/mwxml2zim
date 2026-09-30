# MediaWiki dump → static HTML (proof of concept)

Renders articles from a MediaWiki XML dump (the kind Wikipedia publishes) as
static HTML: one file per page, plus an index linking them together. No ZIM
packaging, no server, no search — see [Limitations](#limitations).

Copyright © 2025 Christian Saliba

## How it works

1. **Phase 1** — `wikitextprocessor` extracts the dump into a per-run SQLite
   cache (main and Template namespaces).
2. Each article's wikitext is parsed with `pre_expand=True`, so the templates
   that change a page's structure (tables, lists, infoboxes) are expanded
   before the walk begins.
3. `htmlHandler.Renderer` walks the parse tree and writes one document per
   page; `out/index.html` links them together.

## Quick start

```bash
pip install -r requirements.txt
python main.py                        # bundled sample dump → out/
python main.py my-dump.xml.bz2 -o out/
```

Options: `-v` prints per-node parse detail, `--log-file PATH` captures the full
DEBUG log. Tested with Python 3.13; the dump must be `.bz2` (enforced by
`wikitextprocessor`).

## Demo

* **Input:** `demo/input.xml.bz2` — a two-page miniature dump (843 bytes)
  written in real Wikipedia-style wikitext: headings, pipe links, lists, a
  `wikitable`, a `<ref>` citation and a `{{convert}}` template.
* **Output:** `demo/output/` — committed exactly as the renderer produced it.
* Regenerate: `python main.py demo/input.xml.bz2 -o demo/output`
* Closer to production data: `appletrainboxtemplates.xml.bz2` holds three real
  articles plus ~160 of their templates.

## Tests

```bash
python -m unittest        # from the repository root
```

Renderer tests covering the document shell, headings and section boundaries,
lists, escaping, bold/italic, plain-text links, inline citations, the template
argument fallback and the index page. Assertions ignore whitespace so layout
changes don't break them, but are strict about content.

## Repository layout

| Path | Role |
| --- | --- |
| `main.py` | CLI, dump pipeline, index generation |
| `htmlHandler.py` | parse tree → HTML document |
| `filewriter.py` | file naming and writing pages |
| `tests/` | renderer tests |
| `demo/` | miniature input dump + committed output |
| `SUMMARY.md` | deeper analysis and roadmap |
| `RefTagsNotes.txt` | design notes for proper citation markers |

## Limitations

* **No ZIM output.** The project used to aim at `.zim` files; it is now a
  static-HTML proof of concept and packaging is out of scope.
* **No images.** `[[File:...]]` captions survive as text, `<gallery>` blocks
  are dropped, and no media is extracted from the dump.
* **Links are plain text.** There is no `<a href>`: the link scheme was
  deferred to a ZIM stage that no longer exists.
* **Templates are only partly expanded.** Expanding the rest needs a template
  analysis pass first; without it, templates render their argument text, which
  shows parameter values (e.g. `{{lang|ang-Latn|Äppel}}` → "ang-Latn Äppel").
* **Scribunto (Lua) templates cannot run** unless `Module:` pages (namespace
  828) are loaded as well; without them, taxoboxes fill with Lua error text.
* **Presentation is minimal.** There is no project stylesheet yet, so tables,
  infoboxes and hatnotes fall back to browser defaults, and prose is not
  wrapped in `<p>` tags.
* **One bad page can abort the run** (writes are error-isolated, parses are
  not), and titles that sanitise to the same filename overwrite each other.
* **Library diagnostics** are printed to stdout by `wikitextprocessor`; they
  are captured during argument re-parsing and logged at DEBUG (`-v`).

## License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
