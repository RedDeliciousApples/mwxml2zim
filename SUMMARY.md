# mwxml2zim — Codebase Summary & Recommended Next Steps

*Generated: 2026-09-27 · branch `main` @ `5c53f21` ("fix some malformed html", 2025-10-29)*

## 1. What this project is

Goal (from `README.md`): convert MediaWiki XML dumps (Wikipedia) into `.zim` files
(the offline format used by Kiwix/ZIM readers).

Current reality: a proof-of-concept that reads a small dump, parses wikitext into a
`wikitextprocessor` parse tree, and appends some HTML into a single file
(`finalfile.html`). **No ZIM output exists yet** — `libzim`/`zimwriterfs`/`zimpy` is
nowhere in `requirements.txt`, and no code writes a ZIM archive.

## 2. Architecture (current)

```
main.py            entry point + dump pipeline + traversal experiments
  ├─ wikitextprocessor (external lib, vendored clone in ./wikitextprocessor, gitignored)
  │    process_dump()  → phase 1: extract pages into SQLite cache
  │    wtp.parse()     → wikitext → WikiNode tree
  ├─ htmlHandler.py   node → HTML fragments (module-level global list)
  └─ filewriter.py    list of strings → one HTML file on close()
```

Pipeline in `main.py`:

1. `print_hi()` hardcodes input `"appletrainboxtemplates.xml.bz2"` (line 159).
2. `process_dump_internal()` runs `process_dump(wtp, path, {0, 10})`, then iterates
   `wtp.get_all_pages([0], False)` through `page_handler()`.
3. `page_handler()` skips non-wikitext and `Template:*`, calls `wtp.parse(page.body)`
   and then three traversals: `traverse()`, `dfs()`, `tohtml()`.
4. `tohtml()` walks top-level children only, dispatching via `DISPATCH` to
   `htmlHandler` (`LIST`, `LEVEL2`, `LEVEL3`, `LEVEL4`, plus raw strings).
5. `htmlHandler.end()` writes everything to `finalfile.html`.

Dependencies (`requirements.txt`): lxml, lupa, regex, dateparser, etc., plus an
editable git install of `wikitextprocessor` pinned at `f26afeb` — which is exactly
the commit of the local clone in `./wikitextprocessor`.

## 3. What works

- Phase‑1 dump extraction (`process_dump`) and page iteration are wired up correctly
  for the current `wikitextprocessor` API (`Page` dataclass with `.body`/`.model`).
- `filewriter.py` produces a well-formed (if minimal) HTML skeleton.
- Level-2/3/4 headings, plain text runs, and simple `*`/`#` lists are dispatched.
- Useful design notes already captured in `RefTagsNotes.txt` for `<ref>` citation
  handling (superscript + `<ol>` backlinks, unique `id` via `set()`).
- Vendored library version matches the pinned requirement (no version drift).

## 4. Critical issues

### 4.1 The project does not run (blocker)

```
$ python main.py
ImportError: cannot import name 'Wtp' from 'wikitextprocessor' (unknown location)
```

- `wikitextprocessor` is **not installed** in the environment (`pip show` → not found).
- The vendored clone `./wikitextprocessor/` sits in the working directory, so Python
  resolves `import wikitextprocessor` to that *directory* as an implicit namespace
  package (it is a `src/`-layout repo with no top-level `__init__.py`), shadowing
  nothing — hence "unknown location".
- The venv at `./.venv` has a broken interpreter (`Could not find platform
  independent libraries … No module named 'encodings'`).

**Fix:** reinstall the dep (`pip install -e ./wikitextprocessor` or the pinned
`-e git+…` from `requirements.txt`) *and* stop importing from a directory that
shadows the package name — e.g. rename the clone dir to `vendor/wikitextprocessor`
or run with the clone on `PYTHONPATH` explicitly. Then repair/recreate `.venv`.

### 4.2 Output is badly mangled (correctness)

Confirmed from the generated `finalfile.html` ("An  is a round, edible…"):

- **Only top-level children are rendered.** `tohtml()` iterates `tree.children` and
  never recurses, so anything nested (emphasis, links, tables, templates, HTML
  tags, paragraphs inside sections) is dropped entirely. `traverse()` walks
  recursively but only counts nodes.
- **Headings render empty.** `htmlHandler.level2(n.sarg)` uses `n.sarg`, but in the
  current library the heading title lives in `node.largs` (`LevelNode`); `sarg` is
  `""` → `<h2></h2>` (visible at the end of `finalfile.html`).
- **`DISPATCH` covers 4 node kinds.** `LINK`, `TEMPLATE`, `TABLE`, `HTML`,
  `ITALIC`, `BOLD`, `URL`, `PREFORMATTED`, `HTML` … silently fall through and lose
  their text (link display text is inside `largs`/`children`, not emitted).
- **Lists lose their content.** `handlelist()` writes `<li>{item.sarg}</li>` —
  `sarg` is the marker (`*`), and `item.children` (the actual text) is never
  rendered. It also recurses on a `LIST_ITEM` and then writes the `<li>` for the
  same node, producing nested `<ul>` inside `<ul>`.
- **`level5`/`level6`/`italic`/`bold`/`hline` exist but are never dispatched.**
- **No HTML escaping** of text nodes: raw `&`, `<`, `>` from wikitext go straight
  into the file.
- **`wtp.parse(page.body)` is called without `pre_expand=True`**, so templates that
  affect document structure (tables, lists, infoboxes) are never expanded — the
  `Template:` pages loaded in phase 1 are therefore unused.

### 4.3 Structural / process problems

| Area | Problem |
|---|---|
| Output model | One global list, one file (`finalfile.html`) for *all* pages; `begin()` is called at import time (`thelist = htmlHandler.begin()`), so state is module-global and unusable if pages are ever processed in subprocesses. |
| Dead/experimental code | `dfs()` (early-`break`/`return`, writes nothing), `traverse()`+`stats`, `load_modules()` (calls `Wtp.process()`, **removed** in the pinned library version), `print_hi()` IDE boilerplate, large commented-out blocks, `switch_dict` sketch. |
| Logging | Dozens of `print()` debug statements per node — O(nodes) output, unusable on a full dump. |
| CLI | No `argparse`; input path, output path and namespaces are hardcoded. |
| Tests / CI | None. No `pyproject.toml`, no lint/format config. |
| Repo hygiene | `.idea/` tracked; `__pycache__/` untracked but not gitignored; output artifact `finalfile.html` not ignored; ~10 MB of sample XML dumps (`Wikipedia-popular-modules.xml` 7.7 MB, `Wikipedia-20230812015758.xml` 2 MB) are committed to git. `.gitignore` has only two lines (`venv`, `wikitextprocessor`). |
| Error handling | `page.body` can be `None` (assert in `parse()`); failures inside dump processing are uncaught; `writeClose()` swallows `OSError` with a print. |
| ZIM goal | Entirely unimplemented — no per-page HTML files, no index, no assets/CSS, no ZIM writer. |

### 4.4 Library-API note

`wtp.node_to_html()` exists in the pinned `wikitextprocessor`, but in this version it
is **not** a wikitext→HTML renderer: `to_html()` (`node_expand.py:208`) just calls
`to_wikitext()` + `ctx.expand()` and has an `XXX` comment that wikitext formatting
still needs to be expanded. So it can't be dropped in as a replacement for
`htmlHandler.py` — the custom tree-walk renderer is still needed (or consider a
different converter, see §6).

## 5. Recommended next steps

### Phase 0 — Make it run (½ day, do first)

1. Recreate/repair `.venv`, then `pip install -r requirements.txt` (or
   `pip install -e ./wikitextprocessor`).
2. Rename the vendored clone to `vendor/wikitextprocessor` (or add it to
   `PYTHONPATH`) so it can't shadow the installed package; update `.gitignore`.
3. Add `__pycache__/`, `*.html` (or `finalfile.html`), `.idea/`, and sample dump
   patterns to `.gitignore`; `git rm --cached` the generated XML/HTML artifacts.
4. Replace per-node `print()` calls with `logging` (single `--verbose` flag).

### Phase 1 — Fix the renderer (2–4 days)

5. Make `tohtml()` a **recursive** walk with a single dispatch table keyed on
   `NodeKind`, covering at least: `LEVEL2‑6`, `LINK`, `URL`, `TEMPLATE`,
   `TABLE/ROW/CELL/CAPTION`, `HTML`, `ITALIC`, `BOLD`, `HLINE`, `LIST/LIST_ITEM`,
   `PREFORMATTED`, `MAGIC_WORD`, and `str`.
   - Drop `dfs()`, `traverse()`, `stats`, `load_modules()`, `print_hi()` — they are
     experiments, and `load_modules()` targets a removed API.
6. Fix heading rendering: use `node.largs` (via `LevelNode.find_content()`) and
   render the title's children recursively, not `node.sarg`.
7. Fix `handlelist()`: render `item.children` recursively inside `<li>`, don't
   re-dispatch on `LIST_ITEM`, and handle definition lists (`;`/`:`).
8. HTML-escape all plain text (`html.escape()`), and emit `<title>`, `<meta
   charset>`, and a real document shell per page.
9. Call `wtp.parse(page.body, pre_expand=True)` so structure-affecting templates
   are expanded; keep phase 1 loading namespaces `{0, 10, 828}` so templates *and*
   Scribunto modules resolve (the `# TODO` in `process_dump_internal` about Module:
   pages is still open).

### Phase 2 — Restructure for output (2–3 days)

10. Replace the module-global `_hlist` with an explicit renderer object
    (`class Renderer: def render(page) -> str`), so each page yields its own HTML
    string instead of appending to a shared list.
11. One output file per page under `out/<sanitized-title>.html`, plus an index;
    write incrementally (streaming) rather than holding the whole dump in memory.
12. Add a CLI: `python -m mwxml2zim dump.xml.bz2 -o out/ [--limit N] [--namespace …]`.
13. Add unit tests: fixture wikitext strings → expected HTML for each node kind
    (headings, links, lists, tables, refs), using `wtp.add_page()` for templates.

### Phase 3 — The actual ZIM (the milestone that matters)

14. Add `libzim` (Python binding) or shell out to `zimwriterfs`; define the ZIM
    layout (main page, index, per-article HTML, favicon, illustration, CSS).
15. Decide the rendering strategy explicitly — three viable options:
    - **A.** Keep the hand-rolled recursive renderer (full control, most work).
    - **B.** Use wikitext→HTML tooling that already does this well
      (e.g. `mwparserfromhell` + a renderer, or Parsoid/php-fiddle outputs) and keep
      `wikitextprocessor` for template/Lua expansion — likely the fastest path to
      correct output.
    - **C.** Reuse an existing offline pipeline (e.g. the approach used by
      Kiwix/`wikipedia_en_*` ZIM builders) and contribute only the missing pieces.
16. Implement `<ref>` handling per `RefTagsNotes.txt` (unique `cite_ref-*` ids,
    backlinks, `<ol>` reference list) — the design is already written down.

### Quick wins (do opportunistically)

- Wire `level5`/`level6`/`italic`/`bold`/`hline` into `DISPATCH`.
- Escape HTML in `_write()` and give the document a real `<title>` (currently
  "Blank HTML Template").
- Delete commented-out code blocks and the IDE boilerplate in `main.py`.
- Untrack `.idea/` and commit a `pyproject.toml` with dependencies + entry point.

## 6. Success criteria for the next milestone

`python -m mwxml2zim appletrainboxtemplates.xml.bz2 -o out/` runs end-to-end with
no traceback, produces one HTML file per page with non-empty headings, intact
paragraph text (no dropped link/template words), escaped entities, and a small
test suite that asserts rendered output for a handful of representative pages.
