"""Input: WebManuscript -- Output: None (writes to disk)."""

import logging
from pathlib import Path

from .manuscript import WebManuscript

logger = logging.getLogger("RSM").getChild("write")


class Writer:
    """Take a WebManuscript and write to disk."""

    def __init__(self, dstpath: Path | None = None) -> None:
        self.web: WebManuscript | None = None
        self.dstpath = Path() if dstpath is None else dstpath

    def write(self, web: WebManuscript) -> None:
        self.web = web
        if not self.dstpath.exists():
            logger.info(f"Creating output directory: {self.dstpath}")
            self.dstpath.mkdir(parents=True, exist_ok=True)
        for path, contents in web.items():
            dest = self.dstpath / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(contents)
