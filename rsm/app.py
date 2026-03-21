"""Applications that execute the steps of the RSM file processing pipeline.

Classes in this module use the steps implemented elsewhere (:mod:`rsm.reader`,
:mod:`rsm.tsparser`, etc) and actually execute those steps, feeding the output of one
step into the next.  The base class for all of these is :class:`RSMApp`, which stores
the sequence of steps and executes them all via a ``run()`` method.

The three main applications provided currently are :func:`make`, :func:`render`, and
:func:`lint`.  These simply instantiate an object of class :class:`FullBuildApp`,
:class:`LinterApp`, :class:`ProcessorApp`, respectively, and call their ``run()``
method.

The functions :func:`make`, :func:`render`, and :func:`lint` can be called directly via
``rsm.make()``, ``rsm.render()``, and ``rsm.lint()``.  They each receive RSM source
(either a string or a path to a file), run the application, and return the result.  For
more control over the execution, or post-execution inspection, instantiate the
appropriate class manually.  For example, this:

.. code-block:: python

   >>> src = "Hello, RSM!"
   >>> html = rsm.build(source=src)

Is essentially equivalent to the following:

.. code-block:: python

   >>> app = FullBuildApp(plain=src)
   >>> html = app.run()

Except that now, ``app`` can be inspected:

.. code-block:: python

   >>> print(app.parser.ast.sexp())
   (Manuscript
     (Paragraph
       (Text)))

The module :mod:`rsm.cli` exposes these apps as command line utilities.

The RSM library code (i.e. all of the previous modules) does not itself set up any
logging facilities.  This is at `recommendation
<https://docs.python.org/3/howto/logging-cookbook.html#adding-handlers-other-than-nullhandler-to-a-logger-in-a-library>`_
of the Python standard library.  Instead, this module uses the functions in
:mod:`rsm.rsmlogger` before executing an application.  In other words, manually handling
RSM source with classes such as :class:`rsm.tsparser.TSParser` or
:class:`rsm.transformer.Transformer` will not issue any logging messages, while calling
the ``run()`` method on an :class:`RSMApp` instance will.

"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import json
import subprocess

from rsm import (
    builder,
    linter,
    pandoc as pandoc_module,
    reader,
    rsmlogger,
    transformer,
    translator,
    tsparser,
    writer,
)
from rsm.tsparser import RSMParserError

from .rsmlogger import GatherHandler

logger = logging.getLogger("RSM")


def _parse_html_to_structured(html: str) -> dict:
    """Parse full HTML document into structured components.

    Parameters
    ----------
    html : str
        Complete HTML document with <html><head>...</head><body>...</body></html>

    Returns
    -------
    dict
        Dictionary with keys 'head', 'body', 'init_script'
    """
    import re

    # Extract head content (everything inside <head>...</head>)
    head_match = re.search(r"<head>(.*?)</head>", html, re.DOTALL)
    if not head_match:
        raise RSMApplicationError("No <head> section found in HTML document")

    head_content = head_match.group(1).strip()

    # Extract body content (everything inside <body>...</body>)
    # Use greedy .* to match the LAST </body> tag, not the first
    # (embedded HTML assets like Plotly charts contain their own </body> tags)
    body_match = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL)
    if not body_match:
        raise RSMApplicationError("No <body> section found in HTML document")

    body_content = body_match.group(1).strip()

    # Extract external script tags from body content and add to head
    # This handles scripts added by HTML assets (like Plotly CDN)
    external_scripts = []
    script_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>'
    re.findall(script_pattern, body_content)

    for script_match in re.finditer(script_pattern, body_content):
        script_tag = script_match.group(0)
        src = script_match.group(1)

        # Only move external scripts (CDN URLs) to head
        if src.startswith(("http://", "https://", "//")):
            external_scripts.append(script_tag)
            # Remove from body content
            body_content = body_content.replace(script_tag, "")

    # Extract execution scripts from after </html> (created by _process_html_with_scripts)
    asset_init_scripts = []
    html_end = html.find("</html>")
    if html_end != -1:
        post_html_content = html[html_end:]

        # Extract CDN URLs for head injection
        src_pattern = r"script_[^.]+\.src\s*=\s*['\"]([^'\"]+)['\"]"
        execution_script_urls = re.findall(src_pattern, post_html_content)

        for url in execution_script_urls:
            if url.startswith(("http://", "https://", "//")):
                script_tag = f'<script src="{url}"></script>'
                external_scripts.append(script_tag)

        # Extract the full IIFE content for execution
        # The IIFE is wrapped in <script>...</script> after </html>
        script_content_pattern = r"<script>\s*(.*?)\s*</script>"
        script_matches = re.findall(
            script_content_pattern, post_html_content, re.DOTALL
        )
        for script_content in script_matches:
            if script_content.strip():
                asset_init_scripts.append(script_content.strip())

    # Add external scripts to head content
    if external_scripts:
        head_content = head_content + "\n" + "\n".join(external_scripts)

    # Clean up any extra whitespace in body content
    body_content = body_content.strip()

    # Combine asset scripts into init_script for frontend execution
    init_script = "\n".join(asset_init_scripts) if asset_init_scripts else ""

    return {"head": head_content, "body": body_content, "init_script": init_script}


class RSMApplicationError(Exception):
    pass


class Task(NamedTuple):
    """A step in a :class:`Pipeline`."""

    name: str
    obj: Any
    run: Callable


class Pipeline:
    """A sequence of :class:`Task` instances executed one after the other."""

    def __init__(self, tasks: list[Task]):
        self.tasks: list[Task] = []
        for t in tasks:
            self.add_task(t)

    def add_task(self, task: Task) -> None:
        """Add a task at the end of the current pipeline."""
        self.tasks.append(task)
        setattr(self, task.name, task.obj)

    def pop_task(self) -> Task:
        """Remove and return the last task."""
        task = self.tasks.pop()
        delattr(self, task.name)
        return task

    def run(self, initial_args: Any = None) -> Any:
        """Execute every task in the pipeline serially."""
        res = initial_args
        for _, _, call in self.tasks:
            if isinstance(res, dict):
                res = call(**res)
            elif isinstance(res, list | tuple):
                res = call(*res)
            elif res is None:
                res = call()
            else:
                res = call(res)
        return res


class RSMApp(Pipeline):
    default_log_level = logging.WARNING

    def __init__(
        self,
        tasks: list[Task] | None = None,
        loglevel: int = default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
    ):
        rsmlogger.config_rsm_logger(loglevel, log_format, log_time, log_lineno)
        logger.info("Application started")
        logger.info("Configuring...")
        # self.config = self.config.configure()
        super().__init__(tasks or [])

    def run(self, initial_args: Any = None) -> str | None:
        try:
            result = super().run(initial_args)
            logger.info("Done.")
        except RSMParserError as e:
            logger.error(f"There was an error: {e}")
            result = ""
        return result

    def _setup_handler(self) -> None:
        target = logging.StreamHandler()
        target.setLevel(logging.WARNING)
        handler = GatherHandler([logging.WARNING], target)
        logger.addHandler(handler)

    @property
    def logs(self) -> list:
        return []


class ParserApp(RSMApp):
    def __init__(
        self,
        srcpath: Path | None = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
        strict: bool = False,
        root_dir: Path | None = None,
    ):
        self._validate_srcpath_and_plain(srcpath, plain)

        tasks = []
        if not plain:
            tasks.append(Task("reader", r := reader.Reader(), lambda: r.read(srcpath)))
        else:
            tasks.append(Task("dummy", None, lambda: plain))

        tasks += [
            Task("parser", p := tsparser.TSParser(), p.parse),
            Task(
                "transformer",
                t := transformer.Transformer(root_dir=root_dir, strict=strict),
                t.transform,
            ),
        ]
        super().__init__(tasks, loglevel, log_format, log_time, log_lineno)

    @staticmethod
    def _validate_srcpath_and_plain(srcpath: Path | str | None, plain: str) -> None:
        if (not srcpath and not plain) or (srcpath and plain):
            raise RSMApplicationError("Must specify exactly one of srcpath, plain")


class LinterApp(ParserApp):
    def __init__(
        self,
        srcpath: Path | None = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
    ):
        super().__init__(
            srcpath, plain, linter.Linter.LINT_LVL, log_format, log_time, log_lineno
        )
        mylinter = linter.Linter()
        self.add_task(Task("linter", mylinter, mylinter.lint))


class ProcessorApp(ParserApp):
    def __init__(
        self,
        srcpath: Path | None = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
        handrails: bool = False,
        add_source: bool = True,
        run_linter: bool = False,
        asset_resolver=None,
        strict: bool = False,
        root_dir: Path | None = None,
    ):
        super().__init__(
            srcpath, plain, loglevel, log_format, log_time, log_lineno, strict, root_dir
        )
        self.asset_resolver = asset_resolver
        if run_linter:
            self.add_task(
                Task("linter", linter_instance := linter.Linter(), linter_instance.lint)
            )

        if not handrails:
            tr = translator.Translator(asset_resolver=asset_resolver)
        else:
            tr = translator.HandrailsTranslator(
                add_source=add_source, asset_resolver=asset_resolver
            )
        self.add_task(Task("translator", tr, tr.translate))


class FullBuildApp(ProcessorApp):
    def __init__(
        self,
        srcpath: Path | None = None,
        plain: str = "",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
        handrails: bool = True,
        add_source: bool = True,
        run_linter: bool = False,
        asset_resolver=None,
        standalone: bool = False,
        write_output: bool = False,
        output_dir: str = ".",
        output_filename: str = "index.html",
        custom_css: str | None = None,
        theme_toggle: bool = True,
        menu_position: str = "left",
        strict: bool = False,
        root_dir: Path | None = None,
    ):
        super().__init__(
            srcpath,
            plain,
            loglevel,
            log_format,
            log_time,
            log_lineno,
            handrails,
            add_source,
            run_linter,
            asset_resolver,
            strict,
            root_dir,
        )
        self.write_output = write_output
        if standalone:
            b = builder.StandaloneBuilder(
                asset_resolver=asset_resolver,
                outname=output_filename,
                custom_css=custom_css,
                theme_toggle=theme_toggle,
                menu_position=menu_position,
            )
        else:
            b = builder.FolderBuilder(
                asset_resolver=asset_resolver,
                outname=output_filename,
                custom_css=custom_css,
                theme_toggle=theme_toggle,
                menu_position=menu_position,
            )
        self.add_task(Task("builder", b, b.build))
        self.add_task(
            Task("writer", w := writer.Writer(dstpath=Path(output_dir)), w.write)
        )

    def run(self, initial_args=None) -> str:
        """Run the build pipeline, optionally writing files to disk.

        If write_output=True, runs all tasks including writer and writes files.
        If write_output=False, skips writer and returns HTML content.
        """
        result = initial_args

        if self.write_output:
            # Run all tasks including writer
            for _, _, call in self.tasks:
                if isinstance(result, dict):
                    result = call(**result)
                elif isinstance(result, list | tuple):
                    result = call(*result)
                elif result is None:
                    result = call()
                else:
                    result = call(result)

            # Writer returns None, so we need to get HTML from the WebManuscript
            # The builder result is stored before writer runs
            for name, obj, _ in self.tasks:
                if name == "builder" and hasattr(obj, "web") and obj.web:
                    return obj.web.html

            logger.error("Builder did not produce WebManuscript")
            return ""
        else:
            # Run all tasks except writer
            for _, _, call in self.tasks[:-1]:
                if isinstance(result, dict):
                    result = call(**result)
                elif isinstance(result, list | tuple):
                    result = call(*result)
                elif result is None:
                    result = call()
                else:
                    result = call(result)

            # The result should now be a WebManuscript from the builder
            if hasattr(result, "html"):
                return result.html
            else:
                logger.error(
                    "Builder did not produce WebManuscript with html attribute"
                )
                return ""


def render(
    source: str = "",
    path: str = "",
    handrails: bool = False,
    add_source: bool = False,
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
    asset_resolver=None,
    strict: bool = False,
    root_dir: Path | None = None,
) -> str:
    return ProcessorApp(
        srcpath=path,
        plain=source,
        handrails=handrails,
        add_source=add_source,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
        asset_resolver=asset_resolver,
        strict=strict,
        root_dir=root_dir,
    ).run()


def lint(
    source: str = "",
    path: str = "",
    handrails: bool = False,
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
    strict: bool = False,
):
    return LinterApp(
        srcpath=path,
        plain=source,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
    ).run()


def build(
    source: str = "",
    path: str = "",
    handrails: bool = True,
    lint: bool = True,
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
    asset_resolver=None,
    structured: bool = False,
    standalone: bool = False,
    write_output: bool = False,
    output_dir: str = ".",
    output_filename: str = "index.html",
    custom_css: str | None = None,
    theme_toggle: bool = True,
    menu_position: str = "left",
    strict: bool = False,
    root_dir: Path | None = None,
) -> str | dict:
    """Process RSM source and optionally write output files.

    Parameters
    ----------
    source : str
        RSM source as a string
    path : str
        Path to RSM source file
    handrails : bool
        Include interactive handrails in output
    lint : bool
        Run linter before building
    loglevel : int
        Logging level
    log_format : str
        Format for log messages
    log_time : bool
        Include timestamps in logs
    log_lineno : bool
        Include line numbers in logs
    asset_resolver : AssetResolver, optional
        Custom asset resolver
    structured : bool
        Return structured dict instead of HTML string
    standalone : bool
        Generate standalone HTML with CDN URLs
    write_output : bool
        Write output files to disk (index.html + static/).
        When False (default), returns HTML without writing files.
        When True, writes files and still returns HTML.
    output_dir : str
        Directory where output files should be written (default: ".")
    output_filename : str
        Name of the main HTML file (default: "index.html")
    theme_toggle : bool
        Include dark mode toggle button and localStorage script (default: True)
    menu_position : str
        Position of handrail context menus: "left" or "right" (default: "left")
    strict : bool
        Raise exception if CST errors are detected after transformation (default: False)

    Returns
    -------
    str or dict
        HTML string (or structured dict if structured=True)
    """
    html_result = FullBuildApp(
        srcpath=path,
        plain=source,
        run_linter=lint,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
        asset_resolver=asset_resolver,
        standalone=standalone,
        write_output=write_output,
        output_dir=output_dir,
        output_filename=output_filename,
        custom_css=custom_css,
        theme_toggle=theme_toggle,
        menu_position=menu_position,
        strict=strict,
        root_dir=root_dir,
    ).run()

    if not structured:
        return html_result

    # Parse HTML into structured components
    return _parse_html_to_structured(html_result)


# ─── Pandoc export ────────────────────────────────────────────────────────────


class _PandocRunner:
    """Pipe a pandoc JSON AST dict to the pandoc subprocess and return the result."""

    def __init__(self, to_format: str, output: str | None = None) -> None:
        self.to_format = to_format
        self.output = output

    def run(self, pandoc_ast: dict) -> str:
        json_str = json.dumps(pandoc_ast)
        cmd = ["pandoc", "--from=json", f"--to={self.to_format}"]
        if self.output:
            cmd += ["-o", self.output]
        try:
            proc = subprocess.run(
                cmd, input=json_str, capture_output=True, text=True, check=True
            )
        except FileNotFoundError:
            raise RSMApplicationError(
                "pandoc executable not found; install pandoc from https://pandoc.org"
            )
        except subprocess.CalledProcessError as e:
            raise RSMApplicationError(f"pandoc failed: {e.stderr}")
        return proc.stdout


def _inject_braiid_typst(typst_source: str, manuscript) -> str:
    """Prepend braiid Typst template to pandoc-generated Typst source."""
    template_path = Path(__file__).parent.parent / "braiid" / "braiid.typ"
    if not template_path.exists():
        return typst_source

    template = template_path.read_text()

    # Extract metadata for the template
    title = getattr(manuscript, "title", "") or ""
    authors = []
    emails = {}
    for child in manuscript.traverse():
        if child.__class__.__name__ == "Author" and getattr(child, "name", None):
            authors.append(child.name)
            email = getattr(child, "email", None)
            if email:
                emails[child.name] = email

    # Build the preamble
    authors_typst = ", ".join(f'"{a}"' for a in authors if a)
    emails_typst = ", ".join(f'"{k}": "{v}"' for k, v in emails.items())
    preamble = template + "\n\n"
    preamble += f'#show: braiid.with(\n'
    preamble += f'  title: [{title}],\n' if title else ''
    preamble += f'  authors: ({authors_typst},),\n' if authors_typst else ''
    preamble += f'  emails: ({emails_typst},),\n' if emails_typst else ''
    preamble += f')\n\n'

    return preamble + typst_source


class PandocExportApp(ParserApp):
    """RSM source → pandoc JSON AST → pandoc subprocess → output string."""

    def __init__(
        self,
        srcpath: Path | None = None,
        plain: str = "",
        to_format: str = "latex",
        output: str | None = None,
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
        strict: bool = False,
    ) -> None:
        super().__init__(srcpath, plain, loglevel, log_format, log_time, log_lineno, strict)
        self._to_format = to_format
        self._output = output

    def run(self, initial_args=None) -> str:
        # The pipeline's dict-unpacking (`call(**res)`) breaks on pandoc JSON AST
        # dicts because they contain hyphen keys (e.g. "pandoc-api-version") that
        # aren't valid Python identifiers. Run the parent pipeline up through the
        # transformer, then call the pandoc steps explicitly.
        manuscript = super().run(initial_args)
        pandoc_ast = pandoc_module.PandocTranslator().translate(manuscript)
        result = _PandocRunner(self._to_format, self._output).run(pandoc_ast)

        # For Typst output, prepend the braiid template and clean up
        if self._to_format == "typst" and self._output is None:
            # Clean up Pandoc Typst output artifacts
            import re as _re
            result = result.replace("\\:", ":")
            result = _re.sub(r'(\d);([.,)\s])', r'\1\2', result)
            result = _re.sub(r'(\d);$', r'\1', result, flags=_re.MULTILINE)
            # Remove duplicate Typst labels (keep first occurrence)
            seen_labels = set()
            lines = result.split('\n')
            deduped = []
            for line in lines:
                m = _re.match(r'^<([a-zA-Z0-9_-]+)>$', line.strip())
                if m:
                    if m.group(1) in seen_labels:
                        continue
                    seen_labels.add(m.group(1))
                deduped.append(line)
            result = '\n'.join(deduped)
            result = _inject_braiid_typst(result, manuscript)

        return result


def pandoc_export(
    source: str = "",
    path: str = "",
    to_format: str = "latex",
    output: str | None = None,
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
    strict: bool = False,
) -> str:
    return PandocExportApp(
        srcpath=path,
        plain=source,
        to_format=to_format,
        output=output,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
        strict=strict,
    ).run()


# ─── Pandoc import ────────────────────────────────────────────────────────────


class PandocImportApp(RSMApp):
    """Any pandoc-supported format → pandoc JSON AST → RSM source text."""

    def __init__(
        self,
        source: str = "",
        path: str = "",
        from_format: str = "markdown",
        loglevel: int = RSMApp.default_log_level,
        log_format: str = "rsm",
        log_time: bool = True,
        log_lineno: bool = True,
    ) -> None:
        if (not source and not path) or (source and path):
            raise RSMApplicationError("Must specify exactly one of source, path")
        super().__init__(tasks=[], loglevel=loglevel, log_format=log_format,
                         log_time=log_time, log_lineno=log_lineno)
        self._source = source
        self._path = path
        self._from_format = from_format

    def run(self, initial_args: Any = None) -> str:
        if self._path:
            cmd = ["pandoc", f"--from={self._from_format}", "--to=json", self._path]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            except FileNotFoundError:
                raise RSMApplicationError(
                    "pandoc executable not found; install pandoc from https://pandoc.org"
                )
            except subprocess.CalledProcessError as e:
                raise RSMApplicationError(f"pandoc failed: {e.stderr}")
        else:
            cmd = ["pandoc", f"--from={self._from_format}", "--to=json"]
            try:
                proc = subprocess.run(
                    cmd, input=self._source, capture_output=True, text=True, check=True
                )
            except FileNotFoundError:
                raise RSMApplicationError(
                    "pandoc executable not found; install pandoc from https://pandoc.org"
                )
            except subprocess.CalledProcessError as e:
                raise RSMApplicationError(f"pandoc failed: {e.stderr}")
        pandoc_ast = json.loads(proc.stdout)
        return pandoc_module.PandocImporter().from_json(pandoc_ast)


def pandoc_import(
    source: str = "",
    path: str = "",
    from_format: str = "markdown",
    loglevel: int = RSMApp.default_log_level,
    log_format: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
) -> str:
    return PandocImportApp(
        source=source,
        path=path,
        from_format=from_format,
        loglevel=loglevel,
        log_format=log_format,
        log_time=log_time,
        log_lineno=log_lineno,
    ).run()
