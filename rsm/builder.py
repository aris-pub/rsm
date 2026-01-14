"""Input: HTML body -- Output: WebManuscript."""

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent

from fs import open_fs
from fs.copy import copy_file

from .manuscript import WebManuscript

logger = logging.getLogger("RSM").getChild("build")


class BaseBuilder(ABC):
    """Use HTML body as a string and create a WebManuscript."""

    def __init__(self, asset_resolver=None, outname: str = "index.html", custom_css: str | None = None) -> None:
        self.body: str | None = None
        self.html: str | None = None
        self.web: WebManuscript | None = None
        self.outname: str = outname
        self.custom_css: str | None = custom_css
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


class HTMLBuilder(BaseBuilder):
    """Base class for builders that output HTML files.

    Produces a single index.html file with /static/ paths for resources.
    Subclasses can override make_html_header() to customize resource URLs.
    """

    body: str
    web: WebManuscript

    def make_main_file(self) -> None:
        html = str(
            "<html>\n\n"
            + self.make_html_header()
            + "\n"
            + self._inject_dark_mode_button(self.body.strip())
            + "\n\n"
            + self.make_html_footer()
            + "</html>\n"
        )
        self.web.writetext(self.outname, html)
        self.web.html = html

    def _inject_dark_mode_button(self, body: str) -> str:
        """Inject dark mode toggle button right after <body> tag."""
        button_html = dedent("""\
            <button class="dark-mode-toggle" onclick="toggleDarkMode()" aria-label="Toggle dark mode">
              <svg class="light-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="4"></circle>
                <path d="M12 2v2"></path>
                <path d="M12 20v2"></path>
                <path d="m4.93 4.93 1.41 1.41"></path>
                <path d="m17.66 17.66 1.41 1.41"></path>
                <path d="M2 12h2"></path>
                <path d="M20 12h2"></path>
                <path d="m6.34 17.66-1.41 1.41"></path>
                <path d="m19.07 4.93-1.41 1.41"></path>
              </svg>
              <svg class="dark-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1 -9 -9"></path>
              </svg>
            </button>
        """)
        # Insert button right after <body> tag
        return body.replace("<body>", f"<body>\n\n{button_html}")


    def make_html_header(self) -> str:
        custom_css_link = ""
        if self.custom_css:
            custom_css_filename = Path(self.custom_css).name
            custom_css_link = f'  <link rel="stylesheet" type="text/css" href="/static/{custom_css_filename}" />\n'

        header = dedent(
            f"""\
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <meta name="generator" content="RSM 0.0.1 https://github.com/leotrs/rsm" />

          <link rel="stylesheet" type="text/css" href="/static/rsm.css" />
          <link rel="stylesheet" type="text/css" href="/static/tooltipster.bundle.css" />
          <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pseudocode@latest/build/pseudocode.min.css">
{custom_css_link}
          <script src="/static/jquery-3.6.0.js"></script>
          <script src="/static/tooltipster.bundle.js"></script>
          <script type="module">
            import {{ onload }} from '/static/onload.js';
            window.addEventListener('load', (ev) => {{window.lsp_ws = onload();}});
          </script>

          <script>
            // Dark mode toggle with localStorage and system preference detection
            (function() {{
              const savedTheme = localStorage.getItem('rsm-theme');
              const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              const isDark = savedTheme === 'dark' || (!savedTheme && prefersDark);

              if (isDark) {{
                document.documentElement.classList.add('dark-theme');
              }}
            }})();

            function toggleDarkMode() {{
              const isDark = document.documentElement.classList.toggle('dark-theme');
              localStorage.setItem('rsm-theme', isDark ? 'dark' : 'light');
            }}
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


class StandaloneBuilder(HTMLBuilder):
    """Builder that produces a single self-contained HTML file.

    Use this builder when the output file needs to work when opened directly
    in a browser (file:// URLs) without a web server. All RSM JavaScript is
    inlined directly in the HTML. Third-party libraries (jQuery, Tooltipster,
    MathJax) are loaded from CDNs.
    """

    CDN_JQUERY = "https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"
    CDN_TOOLTIPSTER_CSS = "https://cdn.jsdelivr.net/npm/tooltipster@4.2.8/dist/css/tooltipster.bundle.min.css"
    CDN_TOOLTIPSTER_JS = "https://cdn.jsdelivr.net/npm/tooltipster@4.2.8/dist/js/tooltipster.bundle.min.js"
    CDN_PSEUDOCODE_CSS = (
        "https://cdn.jsdelivr.net/npm/pseudocode@2.4.1/build/pseudocode.min.css"
    )
    CDN_RSM_CSS = "https://cdn.jsdelivr.net/gh/aris-pub/rsm@main/rsm/static/rsm.css"

    def _get_inline_js(self) -> str:
        """Read the bundled RSM JavaScript for inlining."""
        bundle_path = Path(__file__).parent / "static" / "rsm-standalone.js"
        return bundle_path.read_text()

    def _get_custom_css_inline(self) -> str:
        """Read custom CSS and return as inline <style> tag."""
        if not self.custom_css:
            return ""

        custom_css_path = Path(self.custom_css)
        if custom_css_path.exists():
            css_content = custom_css_path.read_text()
            return f"<style>\n{css_content}\n  </style>\n  "
        else:
            logger.warning(f"Custom CSS file not found: {self.custom_css}")
            return ""

    def make_html_header(self) -> str:
        inline_js = self._get_inline_js()
        custom_css_inline = self._get_custom_css_inline()
        header = f"""\
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="generator" content="RSM 0.0.1 https://github.com/leotrs/rsm" />

  <link rel="stylesheet" type="text/css" href="{self.CDN_RSM_CSS}" />
  <link rel="stylesheet" type="text/css" href="{self.CDN_TOOLTIPSTER_CSS}" />
  <link rel="stylesheet" href="{self.CDN_PSEUDOCODE_CSS}">
  {custom_css_inline}
  <script src="{self.CDN_JQUERY}"></script>
  <script src="{self.CDN_TOOLTIPSTER_JS}"></script>
  <script>
{inline_js}
  </script>
  <script>
    window.addEventListener('load', function() {{ RSM.onload(null, {{keys: false}}); }});
  </script>

  <script>
    // Dark mode toggle with localStorage and system preference detection
    (function() {{
      const savedTheme = localStorage.getItem('rsm-theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isDark = savedTheme === 'dark' || (!savedTheme && prefersDark);

      if (isDark) {{
        document.documentElement.classList.add('dark-theme');
      }}
    }})();

    function toggleDarkMode() {{
      const isDark = document.documentElement.classList.toggle('dark-theme');
      localStorage.setItem('rsm-theme', isDark ? 'dark' : 'light');
    }}
  </script>

  <title>__TITLE_PLACEHOLDER__</title>
</head>
"""
        title = self._extract_title()
        header = header.replace("__TITLE_PLACEHOLDER__", title)
        return header


class FolderBuilder(HTMLBuilder):
    """Builder that outputs an HTML file plus a static/ folder with all assets."""

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

        # Copy custom CSS if provided
        if self.custom_css:
            custom_css_path = Path(self.custom_css)
            if custom_css_path.exists():
                self.web.writetext(
                    f"static/{custom_css_path.name}",
                    custom_css_path.read_text()
                )
            else:
                logger.warning(f"Custom CSS file not found: {self.custom_css}")

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
