# mwxml2zim — Codebase Summary & Progress

*Updated: 2026-09-27 · work on `fix/make-it-run` (run, logging, docs) and `fix/renderer` (renderer, per-page output), based on `main` @ `5c53f21`*

## 1. What this project is

Goal (from `README.md`): convert MediaWiki XML dumps (Wikipedia) into `.zim` files
(the offline format used by Kiwix/ZIM readers).

Current reality: a proof-of-concept that parses a small dump and writes **one HTML
file per page** under `out/`. **No ZIM output exists yet** — no `libzim`/
`zimwriterfs` in `requirements.txt`, and nothing writes a ZIM archive.

## 2. Architecture (current)

```
main.py            CLI (argparse) + logging setup + dump pipeline
  ├─ wikitextprocessor (external lib, vendored clone in ./wikitextprocessor, gitignored)
  │    process_dump()         → phase 1: extract pages into SQLite cache
  │    wtp.parse(body, pre_expand=True) → WikiNode tree (structure-affecting
  │                                        templates expanded first)
  ├─ htmlHandler.py   Renderer: recursive node → HTML, one document per page
  └─ filewriter.py    write_page() → out/<sanitized-title>.html
```

Pipeline in `main.py`:

1. `main()` parses the CLI: `dump` (default `appletrainboxtemplates.xml.bz2`),
   `-o/--output-dir` (default `out`), `-v`, `--log-file`.
2. `process_dump_internal()` runs `process_dump(wtp, path, {0, 10})`, then maps
   `page_handler()` over `wtp.get_all_pages([0], False)`.
3. `page_handler()` skips non-wikitext, `Template:*` and empty pages, parses with
   `pre_expand=True`, then `htmlHandler.render_page(title, tree, wtp)` +
   `filewriter.write_page()` (failures logged, not fatal).
4. `Renderer._render()` accepts a string, a nested list (node arguments) or a
   `WikiNode`; `HANDLERS` dispatches per `NodeKind` and unknown kinds fall back to
   their children so no text is lost. Template/link arguments are raw wikitext and
   get re-parsed by `_render_fragment()`.

Dependencies (`requirements.txt`): lxml, lupa, regex, dateparser, etc., plus
`wikitextprocessor` installed editable from the local clone, pinned at `f26afeb`.

## 3. Progress

### Phase 0 — Make it run ✅

- `.venv` repaired (interpreter repointed, `.bak` backup); run with
  `.\.venv\Scripts\python.exe main.py` — exit 0, 3 pages, 9 INFO lines.
  (System `python` still fails: the vendored clone shadows the package name.)
- stdout/stderr forced to UTF-8 so Windows consoles survive `₂` and friends.
- `print()` spam replaced by `logging`: root at DEBUG, console INFO (DEBUG with
  `-v`), `--log-file` gets timestamped DEBUG. The library's own stdout parse
  warnings are captured and logged as DEBUG lines instead.

### Phase 1 — Fix the renderer ✅

- One recursive walk with a `HANDLERS` table covering every `NodeKind`.
- Headings read their title from `node.largs` **and render their section content**;
  lists emit real `<ul>/<ol>/<dl>` containing item text (incl. `;`/`:` definition
  lists); all text is HTML-escaped; each page gets a document shell with `<title>`,
  charset and a `<style>`.
- `pre_expand=True`, so infoboxes and other structure-affecting templates become
  real nodes (the Apple page contains a `<table>`).
- Template/parser-function/argument nodes fall back to their argument text with the
  `name=` label dropped (keeps `{{cite web|...}}` prose); `<ref>` blocks render
  inline in `<span class="reference">` as an interim measure.
- Links render as display text only (URL scheme deferred to the ZIM stage);
  `Category:` links are dropped, `File:`/`Image:` keep their caption but not
  layout/technical arguments (`thumb`, `200px`, `alt=` …).
- Dead code removed: `dfs()`, `tohtml()`, `DISPATCH`, `load_modules()`,
  `print_hi()`, commented-out blocks; stale `finalfile.html` deleted, `out/`
  gitignored.

### Phase 2 — Restructure for output 🟡

- ✅ Per-page output (`filewriter.write_page`), explicit `Renderer` object (no
  module-global list), `argparse` CLI with `-o`.
- ☐ Index page, and decide how articles link to each other.
- ☐ Unit tests: fixture wikitext → expected HTML per node kind.

## 4. Remaining issues

### 4.1 Rendering quality

- **Template argument fallback is generic.** `{{lang|ang-Latn|Äppel}}` shows the
  language code too — the biggest remaining prose artifact. Fix with a template-
  override table (`lang`, `transl`, `ipa`, citations) or selective expansion.
- **No `<p>` tags**: wikitext paragraphs are plain text runs (the parser does not
  model them), so prose wraps oddly in browsers.
- Fragment re-parsing has three traps, documented in `htmlHandler.py`: bare URLs
  re-parse into URL nodes (infinite recursion — `_url()` deliberately doesn't),
  line-start markers (`*aplaz`) become lists, untrimmed arguments become `<pre>`.
- **Images are not downloaded**; `File:` captions stay as text and `<gallery>` and
  friends are dropped.

### 4.2 Structural / process

| Area | Problem |
|---|---|
| Robustness | One malformed page aborts the whole run (no per-page `try/except`); sanitized titles can collide (`A:B` vs `A_B`). |
| Modules | Phase 1 loads namespaces `{0, 10}` only; the `Module:` TODO in `process_dump_internal` is open, so Lua templates cannot expand. |
| Tests / CI | None. No `pyproject.toml`, no lint/format config. |
| Repo hygiene | `.idea/` tracked; ~10 MB of sample XML dumps committed to git. |
| ZIM goal | Unimplemented — no index, no assets/CSS, no ZIM writer. |

### 4.3 Library-API note

`wtp.node_to_html()` exists in the pinned `wikitextprocessor` but is **not** a
wikitext→HTML renderer (`to_html()` just calls `to_wikitext()` + `ctx.expand()`
and carries an `XXX` comment), so `htmlHandler.py` cannot be replaced by it.

## 5. Recommended next steps

### Finish Phase 2 (small)

1. Template overrides (`lang`, citations) or selective expansion — by far the
   biggest quality win for the effort.
2. Per-page `try/except` + failure count in `page_handler`; filename-collision
   handling in `filewriter`.
3. Renderer tests (headings, links, lists, tables, refs); optionally drop
   `traverse()`/`stats`, which only feeds the node-count line.
4. Index page, `pyproject.toml` with an entry point, untrack `.idea/`.

### Phase 3 — The actual ZIM (the milestone that matters)

5. Add `libzim` (Python binding) or shell out to `zimwriterfs`; define the ZIM
   layout (main page, index, per-article HTML, favicon, illustration, CSS).
6. Decide the rendering strategy explicitly — three viable options:
   - **A.** Keep the hand-rolled recursive renderer (full control, most work).
   - **B.** Use wikitext→HTML tooling that already does this well
     (`mwparserfromhell` + a renderer, or Parsoid outputs) and keep
     `wikitextprocessor` for template/Lua expansion — likely the fastest route
     to correct output.
   - **C.** Reuse an existing offline pipeline (the approach used by the Kiwix
     `wikipedia_en_*` ZIM builders) and contribute only the missing pieces.
7. Implement `<ref>` handling per `RefTagsNotes.txt` (unique `cite_ref-*` ids,
   backlinks, `<ol>` reference list) — the design is already written down.
8. Load namespaces `{0, 10, 828}` and wire Module: pages so Lua templates resolve.

## 6. Success criteria for the next milestone

`python main.py <full-dump>.xml.bz2 -o out/` runs end-to-end with no traceback,
one HTML file per page with non-empty headings, intact paragraph text (no dropped
link/template words), escaped entities, and a small test suite for representative
pages.
