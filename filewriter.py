"""Writes rendered HTML documents to disk."""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Characters that are not allowed in file names on Windows (plus the
# control characters); titles such as "AC/DC" or "Star Trek: Voyager"
# contain them and get an underscore instead.
UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def page_filename(title: str) -> str:
    """Turn a page title into a file name, e.g. 'AC/DC' -> 'AC_DC.html'."""
    filename = UNSAFE_FILENAME_CHARS.sub("_", title).strip(" .")
    if not filename:
        filename = "untitled"
    return filename + ".html"


def write_page(output_dir: str, title: str, document: str) -> Path | None:
    """Write one rendered page into output_dir and return its path.

    Returns None when the file could not be written, so that the rest of
    the dump keeps going; the failure is logged either way.
    """
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / page_filename(title)

    try:
        path.write_text(document, encoding="utf-8")
    except OSError:
        logger.exception("Could not write %s", path)
        return None

    logger.debug("Wrote %s", path)
    return path
