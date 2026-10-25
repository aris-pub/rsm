"""Input: WebManuscript -- Output: None (writes to disk)."""

import logging
import shutil
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

        self._copy_assets(web)

    def _copy_assets(self, web: WebManuscript) -> None:
        """Copy referenced user assets into the output folder so it is
        self-contained and can be moved. Media is copied as-is (binaries
        included); the in-memory tree above holds only text."""
        out_root = self.dstpath.resolve()
        for source, rel_dest in web.assets:
            dest = (self.dstpath / rel_dest).resolve()
            # Keep every asset inside the output folder. A path that escapes it
            # (e.g. "../shared/x.png") cannot be made self-contained here.
            if out_root not in dest.parents and dest != out_root:
                logger.warning(
                    f"Asset {rel_dest} resolves outside the output folder; not copied"
                )
                continue
            if not source.exists():
                logger.warning(f"Referenced asset not found, not copied: {source}")
                continue
            if source.resolve() == dest:
                continue  # output dir is the source dir; the file is already here
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, dest)
