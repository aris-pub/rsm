"""Input: HTML body -- Output: WebManuscript."""

import base64
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent

from .manuscript import WebManuscript

logger = logging.getLogger("RSM").getChild("build")


class BaseBuilder(ABC):
    """Use HTML body as a string and create a WebManuscript."""

    _SCRIPT_SRC_RE = re.compile(
        r'<script\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>\s*</script>'
    )

    def __init__(
        self,
        asset_resolver=None,
        outname: str = "index.html",
        custom_css: str | None = None,
        theme_toggle: bool = True,
        menu_position: str = "left",
    ) -> None:
        self.body: str | None = None
        self.html: str | None = None
        self.web: WebManuscript | None = None
        self.outname: str = outname
        self.custom_css: str | None = custom_css
        self.theme_toggle: bool = theme_toggle
        self.menu_position: str = menu_position
        # Default to disk-based asset resolver if none provided
        if asset_resolver is None:
            from .asset_resolver import AssetResolverFromDisk

            asset_resolver = AssetResolverFromDisk()
        self.asset_resolver = asset_resolver

    def deduplicate_scripts(self, body: str) -> str:
        """Remove duplicate <script src="..."> tags, keeping the first occurrence of each URL."""
        seen = set()

        def _replace(match):
            url = match.group(1)
            if url in seen:
                return ""
            seen.add(url)
            return match.group(0)

        return self._SCRIPT_SRC_RE.sub(_replace, body)

    def build(self, body: str, src: Path = None) -> WebManuscript:
        logger.info("Building...")
        self.body = self.deduplicate_scripts(body)
        self.web = WebManuscript(src)
        self.web.body = self.body

        logger.debug("Searching required static assets...")
        self.required_assets: list[Path] = []
        self.find_required_assets()

        logger.debug("Building main file...")
        self.make_main_file()
        return self.web

    @abstractmethod
    def make_main_file(self) -> None:
        pass

    # Binary media (images, video) is referenced by relative path and left in
    # place rather than bundled into static/ (see test_multiple_files_assets).
    # Excluding it here keeps it out of mount_required_assets, which would
    # otherwise read the bytes only to write them back as text.
    _UNBUNDLED_MEDIA_SUFFIXES = frozenset(
        {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".webm", ".avi", ".mov"}
    )

    def find_required_assets(self) -> None:
        self.required_assets = [
            Path(x)
            for x in re.findall(r'src="(.*?)"', str(self.body))
            if not x.startswith(("http://", "https://"))
            and Path(x).suffix.lower() not in self._UNBUNDLED_MEDIA_SUFFIXES
        ]


class HTMLBuilder(BaseBuilder):
    """Base class for builders that output HTML files.

    Produces a single index.html file with /static/ paths for resources.
    Subclasses can override make_html_header() to customize resource URLs.
    """

    body: str
    web: WebManuscript

    def make_main_file(self) -> None:
        body = self.body.strip()
        if self.theme_toggle:
            body = self._inject_dark_mode_button(body)

        # Extract data-accent and data-lang from body tag and move to html tag
        accent_match = re.search(r'<body[^>]*data-accent="([^"]*)"', body)
        accent_attr = f' data-accent="{accent_match.group(1)}"' if accent_match else ""

        lang_match = re.search(r'<body[^>]*data-lang="([^"]*)"', body)
        lang_value = lang_match.group(1) if lang_match else "en"

        html = str(
            f'<!DOCTYPE html>\n<html lang="{lang_value}"{accent_attr}>\n\n'
            + self.make_html_header()
            + "\n"
            + body
            + "\n\n"
            + self.make_html_footer()
            + "</html>\n"
        )
        self.web.writetext(self.outname, html)
        self.web.html = html

    def _inject_dark_mode_button(self, body: str) -> str:
        """No-op: light/dark is now a control in the sidebar's Reading tab, not a
        standalone chrome button. Kept so existing call sites stay valid."""
        return body

    def make_html_header(self) -> str:
        custom_css_link = ""
        if self.custom_css:
            custom_css_filename = Path(self.custom_css).name
            custom_css_link = f'  <link rel="stylesheet" type="text/css" href="/static/{custom_css_filename}" />\n'

        menu_position_style = ""
        if self.menu_position == "right":
            menu_position_style = dedent("""\

          <style>
            .manuscriptwrapper .hr .hr-menu-zone .hr-menu {
              left: 32px !important;
            }
            .manuscriptwrapper .hr.hr-offset .hr-menu-zone .hr-menu {
              left: 16px !important;
            }
          </style>
        """)

        dark_mode_script = ""
        if self.theme_toggle:
            dark_mode_script = dedent("""\

          <script>
            // Apply saved reading preferences before first paint (typeface,
            // size, line height, width, and light/dark). The interactive
            // controls live in the sidebar's Reading tab.
            (function() {
              var prefs = {};
              try { prefs = JSON.parse(localStorage.getItem('rsm-reading') || '{}') || {}; } catch (e) {}
              var root = document.documentElement;
              ['typeface', 'size', 'leading', 'measure'].forEach(function(c) {
                if (prefs[c]) root.setAttribute('data-reading-' + c, prefs[c]);
              });
              var theme = prefs.theme || localStorage.getItem('rsm-theme');
              var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              if (theme === 'dark' || (!theme && prefersDark)) {
                root.classList.add('dark-theme');
              }
            })();
          </script>
        """)

        header = dedent(
            f"""\
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <meta name="generator" content="RSM 0.0.1 https://github.com/leotrs/rsm" />

          <link rel="stylesheet" type="text/css" href="/static/braiid.css" />
          <link rel="stylesheet" type="text/css" href="/static/tooltipster.bundle.css" />
          <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pseudocode@latest/build/pseudocode.min.css">
{custom_css_link}{menu_position_style}
          <script src="/static/jquery-3.6.0.js"></script>
          <script src="/static/tooltipster.bundle.js"></script>
          <script type="module">
            import {{ onload }} from '/static/onload.js';
            window.addEventListener('load', (ev) => {{window.lsp_ws = onload();}});
          </script>{dark_mode_script}

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

    Use this builder when the output file needs to work when opened directly in
    a browser (file:// URLs) with no web server and no network. The RSM bundle
    and every third-party library it needs (temml, jQuery, Tooltipster,
    pseudocode) are inlined from pinned copies vendored under static/. The math
    font Temml.woff2 is embedded as a data URI inside the temml CSS, and the
    Google Fonts and KaTeX @import rules that braiid.css and pseudocode.min.css
    would otherwise pull over the network are stripped.

    MathJax is deliberately not inlined. It is only an unreachable fallback once
    temml is always present, and it weighs several megabytes. Its loader stays
    in the RSM bundle as dead code that never runs in a standalone file.
    """

    # Pinned versions of the third-party assets vendored under static/. Change a
    # version here only together with re-vendoring the matching file.
    TEMML_VERSION = "0.13.4"
    JQUERY_VERSION = "3.6.0"
    TOOLTIPSTER_VERSION = "4.2.8"
    PSEUDOCODE_VERSION = "2.4.1"

    _STATIC = Path(__file__).parent / "static"
    _BRAIID_CSS = Path(__file__).parent.parent / "braiid" / "braiid.css"

    # Each @import in braiid.css sits on its own line. Two pull Google Fonts over
    # the network and one duplicates the pygments stylesheet this builder already
    # inlines. Drop them all so the file needs nothing external. Text falls back
    # to the family stacks braiid already declares.
    _IMPORT_LINE_RE = re.compile(r"(?m)^[ \t]*@import\b[^\n]*\n?")
    # pseudocode.min.css is minified onto one line and opens with an @import of
    # KaTeX CSS from cdnjs. temml renders MathML, not KaTeX spans, so that CSS is
    # unused here. This matches an external @import inside a single line.
    _EXTERNAL_IMPORT_RE = re.compile(
        r"@import\s+url\(\s*['\"]?\s*https?://[^)]*\)[^;]*;"
    )
    # Temml-Latin-Modern.css declares a Latin Modern Math @font-face pointing at
    # latinmodernmath.woff2, a file the temml package does not ship (it 404s on
    # the CDN too). Drop the rule so the standalone file carries no dead font
    # reference. Math renders in the browser math font, as it did online.
    _LMM_FONTFACE_RE = re.compile(
        r"@font-face\s*\{[^}]*latinmodernmath[^}]*\}", re.IGNORECASE
    )

    def _read_static(self, name: str) -> str:
        return (self._STATIC / name).read_text()

    @staticmethod
    def _style(css: str) -> str:
        return f"  <style>\n{css}\n  </style>\n"

    @staticmethod
    def _script(js: str) -> str:
        return f"  <script>\n{js}\n  </script>\n"

    def _get_inline_js(self) -> str:
        """Read the bundled RSM JavaScript for inlining."""
        return self._read_static("rsm-standalone.js")

    def _get_braiid_css_inline(self) -> str:
        return self._IMPORT_LINE_RE.sub("", self._BRAIID_CSS.read_text())

    def _get_pseudocode_css_inline(self) -> str:
        return self._EXTERNAL_IMPORT_RE.sub("", self._read_static("pseudocode.min.css"))

    def _get_temml_css_inline(self) -> str:
        """Temml's Latin-Modern CSS with the font embedded so it needs no network."""
        css = self._read_static("Temml-Latin-Modern.css")
        font_b64 = base64.b64encode((self._STATIC / "Temml.woff2").read_bytes()).decode(
            "ascii"
        )
        css = css.replace(
            "url('Temml.woff2')", f"url(data:font/woff2;base64,{font_b64})"
        )
        return self._LMM_FONTFACE_RE.sub("", css)

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

    def _get_pygments_css_inline(self) -> str:
        """Read pygments.css for inlining in standalone output."""
        css_path = self._STATIC / "pygments.css"
        if css_path.exists():
            return f"<style>\n{css_path.read_text()}\n  </style>\n  "
        return ""

    def make_html_header(self) -> str:
        menu_position_style = ""
        if self.menu_position == "right":
            menu_position_style = """
  <style>
    .manuscriptwrapper .hr .hr-menu-zone .hr-menu {
      left: 32px !important;
    }
    .manuscriptwrapper .hr.hr-offset .hr-menu-zone .hr-menu {
      left: 16px !important;
    }
  </style>
"""

        dark_mode_script = ""
        if self.theme_toggle:
            dark_mode_script = """
  <script>
    // Apply saved reading preferences before first paint; controls live in the
    // sidebar's Reading tab.
    (function() {
      var prefs = {};
      try { prefs = JSON.parse(localStorage.getItem('rsm-reading') || '{}') || {}; } catch (e) {}
      var root = document.documentElement;
      ['typeface', 'size', 'leading', 'measure'].forEach(function(c) {
        if (prefs[c]) root.setAttribute('data-reading-' + c, prefs[c]);
      });
      var theme = prefs.theme || localStorage.getItem('rsm-theme');
      var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (theme === 'dark' || (!theme && prefersDark)) {
        root.classList.add('dark-theme');
      }
    })();
  </script>
"""

        # temml must define window.temml before the RSM bundle runs, and the
        # katex alias lets pseudocode find a renderer without going through the
        # on-demand loader (which would otherwise inject a CDN script).
        parts = [
            "<head>\n",
            '  <meta charset="utf-8" />\n',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n',
            '  <meta name="generator" content="RSM 0.0.1 https://github.com/leotrs/rsm" />\n\n',
            self._style(self._get_braiid_css_inline()),
            self._style(self._read_static("tooltipster.bundle.min.css")),
            self._style(self._get_pseudocode_css_inline()),
            self._style(self._get_temml_css_inline()),
            "  ",
            self._get_pygments_css_inline(),
            self._get_custom_css_inline(),
            menu_position_style,
            "\n",
            self._script(self._read_static("jquery-3.6.0.min.js")),
            self._script(self._read_static("tooltipster.bundle.min.js")),
            self._script(self._read_static("temml.min.js")),
            "  <script>window.katex = window.katex || window.temml;</script>\n",
            self._script(self._read_static("pseudocode.min.js")),
            self._script(self._get_inline_js()),
            "  <script>\n"
            "    window.addEventListener('load', function() { RSM.onload(null, {keys: false}); });\n"
            "  </script>",
            dark_mode_script,
            f"\n\n  <title>{self._extract_title()}</title>\n",
            "</head>\n",
        ]
        return "".join(parts)


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

        self.web.makedir("static")
        for fn in source_path.iterdir():
            if fn.suffix in {".js", ".css"}:
                self.web.writetext(f"static/{fn.name}", fn.read_text())

        # Copy BRAIID CSS from braiid/ directory
        braiid_css_path = working_path.parent / "braiid" / "braiid.css"
        if braiid_css_path.exists():
            self.web.writetext("static/braiid.css", braiid_css_path.read_text())
        else:
            logger.warning(f"BRAIID CSS not found at: {braiid_css_path}")

        # Copy custom CSS if provided
        if self.custom_css:
            custom_css_path = Path(self.custom_css)
            if custom_css_path.exists():
                self.web.writetext(
                    f"static/{custom_css_path.name}", custom_css_path.read_text()
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
