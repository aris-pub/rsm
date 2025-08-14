"""Input: HTML body -- Output: WebManuscript."""

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent
from typing import Optional

from fs import open_fs
from fs.copy import copy_file
from icecream import ic

from .manuscript import WebManuscript

logger = logging.getLogger("RSM").getChild("build")


class BaseBuilder(ABC):
    """Use HTML body as a string and create a WebManuscript."""

    def __init__(self, asset_resolver=None) -> None:
        self.body: Optional[str] = None
        self.html: Optional[str] = None
        self.web: Optional[WebManuscript] = None
        self.outname: str = "index.html"
        # Default to disk-based asset resolver if none provided
        if asset_resolver is None:
            from .asset_resolver import AssetResolverFromDisk
            asset_resolver = AssetResolverFromDisk()
        self.asset_resolver = asset_resolver

    def build(self, body: str, src: Path = None) -> WebManuscript:
        logger.info("Building...")
        self.body = body
        self.web = WebManuscript(src)
        self.web.body = body

        logger.debug("Searching required static assets...")
        self.required_assets: list[Path] = []
        self.find_required_assets()

        logger.debug("Building main file...")
        self.make_main_file()
        return self.web

    @abstractmethod
    def make_main_file(self) -> None:
        pass

    def find_required_assets(self) -> None:
        self.required_assets = [
            Path(x) for x in re.findall(r'src="(.*?)"', str(self.body))
        ]


class SingleFileBuilder(BaseBuilder):
    body: str
    web: WebManuscript

    def make_main_file(self) -> None:
        html = str(
            "<html>\n\n"
            + self.make_html_header()
            + "\n"
            + self.body.strip()
            + "\n\n"
            + self.make_html_footer()
            + "</html>\n"
        )
        self.web.writetext(self.outname, html)
        self.web.html = html

    def make_html_header(self) -> str:
        header = dedent(
            """\
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <meta name="generator" content="RSM 0.0.1 https://github.com/leotrs/rsm" />

          <link rel="stylesheet" type="text/css" href="/static/rsm.css" />
          <link rel="stylesheet" type="text/css" href="/static/tooltipster.bundle.css" />
          <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pseudocode@latest/build/pseudocode.min.css">

          <script src="/static/jquery-3.6.0.js"></script>
          <script src="/static/tooltipster.bundle.js"></script>
          <script type="module">
            import { onload } from '/static/onload.js';
            window.addEventListener('load', (ev) => {window.lsp_ws = onload();});
          </script>

          <title>__TITLE_PLACEHOLDER__</title>
        </head>
        """
        )
        title = self._extract_title()
        header = header.replace("__TITLE_PLACEHOLDER__", title)
        return header

    def make_html_footer(self) -> str:
        return ""

    def _extract_title(self) -> str:
        mobj = re.search(r"<h1>(.*?)</h1>", self.body)
        if mobj is None:
            return ""
        else:
            return mobj.group(1)


class FullBuilder(SingleFileBuilder):
    def build(self, body: str, src: Path = None) -> WebManuscript:
        super().build(body, src)
        logger.debug("Moving default RSM assets...")
        self.mount_static()
        if self.required_assets:
            logger.debug("Moving user assets...")
            self.mount_required_assets()
        return self.web

    def mount_static(self) -> None:
        working_path = Path(__file__).parent.absolute()
        source_path = (working_path / "static").resolve()
        source = open_fs(str(source_path))

        self.web.makedir("static")
        for fn in [
            fn for fn in source.listdir(".") if Path(fn).suffix in {".js", ".css"}
        ]:
            copy_file(source, fn, self.web, f"static/{fn}")

    def mount_required_assets(self) -> None:
        """Mount required assets using the asset resolver.
        
        Technical Debt Note: This method demonstrates the architectural inconsistency
        where assets use the resolver system but the main RSM file still uses
        direct filesystem access via Reader class. This should be unified in future
        refactoring.
        """
        for fn in self.required_assets:
            asset_content = self.asset_resolver.resolve_asset(str(fn))
            if asset_content is not None:
                self.web.writetext(f"static/{fn.name}", asset_content)
            else:
                logger.warning(f"Unable to resolve required asset: {fn}")
