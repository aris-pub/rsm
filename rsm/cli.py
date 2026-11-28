"""RSM command line utilities.

The apps implemented in :mod:`rsm.app` are hereby exposed to the user as command line
utilities.

"""

import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Callable
from importlib.metadata import version
from pathlib import Path

import livereload

from rsm import app


def _add_common_args(
    parser: ArgumentParser,
    *,
    handrails: bool = False,
    page_style: bool = False,
    verbose: bool = True,
    strict: bool = True,
) -> None:
    """Add the arguments shared by the subcommands that read one RSM source.

    The keyword flags add the options that only some subcommands use.
    """
    parser.add_argument(
        "src",
        help="RSM source path",
    )

    input_opts = parser.add_argument_group("input control")
    input_opts.add_argument(
        "-c",
        "--string",
        help="interpret src as a source string, not a path",
        action="store_true",
    )

    output_opts = parser.add_argument_group("output control")
    if handrails:
        output_opts.add_argument(
            "-r",
            "--handrails",
            help="output handrails",
            action="store_true",
        )
    if page_style:
        output_opts.add_argument(
            "--css",
            help="path to custom CSS file",
            type=str,
            default=None,
        )
        output_opts.add_argument(
            "--menu-right",
            help="position handrail context menus to the right instead of left",
            action="store_true",
        )

    log_opts = parser.add_argument_group("logging control")
    if verbose:
        log_opts.add_argument(
            "-v",
            "--verbose",
            help="verbosity",
            action="count",
            default=0,
        )
    log_opts.add_argument(
        "--log-no-timestamps",
        dest="log_time",
        help="exclude timestamp in logs",
        action="store_false",
    )
    log_opts.add_argument(
        "--log-no-lineno",
        dest="log_lineno",
        help="exclude line numbers in logs",
        action="store_false",
    )
    log_opts.add_argument(
        "--log-format",
        help="format for logs",
        choices=["plain", "rsm", "json", "lint"],
        default="rsm",
    )
    if strict:
        log_opts.add_argument(
            "--strict",
            help="raise exception on CST errors (halt build on syntax errors)",
            action="store_true",
        )


def _run_app(func: Callable, args: Namespace, print_output: bool = True) -> int:
    """Run an RSM app function with parsed arguments."""
    kwargs = {
        "handrails": args.handrails,
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
        "strict": args.strict,
    }
    if getattr(args, "sidebar", False):
        kwargs["sidebar"] = True
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src
    output = func(**kwargs)
    if print_output and output:
        print(output)
    return 0


def _cmd_export(args: Namespace) -> int:
    """Handle 'rsm export' subcommand."""
    kwargs = {
        "to_format": args.to,
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
        "strict": args.strict,
    }
    if args.output:
        kwargs["output"] = args.output
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src
    try:
        result = app.pandoc_export(**kwargs)
    except app.RSMApplicationError as exc:
        print(f"export error: {exc}", file=sys.stderr)
        return 1
    if result is None:
        return 1
    if result and not args.output:
        print(result)
    return 0


def _cmd_import(args: Namespace) -> int:
    """Handle 'rsm import' subcommand."""
    logkw = {
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
    }
    if args.string:
        result = app.pandoc_import(source=args.src, from_format=args.frm, **logkw)
    else:
        from rsm.importer import ImporterError, is_archive

        src = Path(args.src)
        if src.is_dir() or is_archive(src) or args.frm == "latex":
            try:
                result = app.import_project(
                    str(src), main=args.main, from_format=args.frm, **logkw
                )
            except ImporterError as exc:
                print(f"import error: {exc}", file=sys.stderr)
                return 1
        else:
            result = app.pandoc_import(path=args.src, from_format=args.frm, **logkw)
    if result:
        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result)
    return 0


def _cmd_render(args: Namespace) -> int:
    """Handle 'rsm render' subcommand."""
    return _run_app(app.render, args, print_output=not args.silent)


def _cmd_check(args: Namespace) -> int:
    """Handle 'rsm check' subcommand."""
    kwargs = {
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
    }
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src
    app.lint(**kwargs)
    return 0


def _cmd_parse(args: Namespace) -> int:
    """Handle 'rsm parse' subcommand - output AST as JSON."""
    import json

    kwargs = {
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
        "strict": args.strict,
    }
    if args.string:
        kwargs["plain"] = args.src
    else:
        kwargs["srcpath"] = Path(args.src)

    # Parse the document
    parser = app.ParserApp(**kwargs)
    manuscript = parser.run()
    if manuscript is None:
        return 1

    # Serialize to JSON
    ast_dict = manuscript.to_dict()
    json_output = json.dumps(ast_dict, indent=2 if args.pretty else None)

    print(json_output)
    return 0


def _parse_output_flag(value: str) -> tuple[str, str | None]:
    """Parse -o flag into (output_dir, output_filename).

    Cases:
    - "myfile" -> (".", "myfile.html")
    - "myfile.html" -> (".", "myfile.html")
    - "build/" -> ("build", None)  # None means derive from input
    - "build/myfile" -> ("build", "myfile.html")
    """
    if "/" not in value:
        # Just a filename
        if not value.endswith(".html"):
            return (".", f"{value}.html")
        else:
            return (".", value)
    elif value.endswith("/"):
        # Just a directory, filename should be derived from input
        return (value.rstrip("/"), None)
    else:
        # Directory and filename
        parts = value.rsplit("/", 1)
        filename = parts[1]
        if not filename.endswith(".html"):
            filename = f"{filename}.html"
        return (parts[0], filename)


def _cmd_build(args: Namespace) -> int:
    """Handle 'rsm build' subcommand."""
    output_dir = "."
    output_filename = None

    if args.output:
        output_dir, output_filename = _parse_output_flag(args.output)

    # Derive output filename from input if not specified
    if output_filename is None:
        if args.string:
            # For string input, default to index.html
            output_filename = "index.html"
        else:
            # For file input, use input filename with .html extension
            from pathlib import Path

            input_path = Path(args.src)
            output_filename = f"{input_path.stem}.html"

    # Auto-detect CSS file if not specified via --css flag
    custom_css = args.css
    if custom_css is None and not args.string:
        # Look for a CSS file with the same name as the input file
        from pathlib import Path

        input_path = Path(args.src)
        auto_css_path = input_path.with_suffix(".css")
        if auto_css_path.exists():
            custom_css = str(auto_css_path)

    kwargs = {
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
        "write_output": True,
        "standalone": args.standalone,
        "output_dir": output_dir,
        "output_filename": output_filename,
        "custom_css": custom_css,
        "theme_toggle": not args.no_theme_toggle,
        "menu_position": "right" if args.menu_right else "left",
        "strict": args.strict,
        "sidebar": args.sidebar,
    }
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src

    app.build(**kwargs)
    return 0


def _cmd_init(args: Namespace) -> int:
    """Handle 'rsm init' subcommand - scaffold a new RSM project."""
    from pathlib import Path

    # Get current directory
    project_dir = Path.cwd()

    # Check if directory already has RSM files
    existing_rsm = list(project_dir.glob("*.rsm"))
    if existing_rsm and not args.force:
        print(
            f"Error: Directory already contains RSM files: {', '.join(f.name for f in existing_rsm)}"
        )
        print("Use --force to initialize anyway")
        return 1

    # Interactive prompts
    print("Initializing new RSM project...\n")

    # Ask for filename
    default_filename = "document"
    filename_input = input(f"Main RSM filename [{default_filename}]: ").strip()
    filename = filename_input if filename_input else default_filename

    # Ask for author
    author_input = input("Author name(s): ").strip()
    author = author_input if author_input else "Author Name"

    # Create assets directory and fetch/copy Aris logo
    assets_dir = project_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Try to fetch latest Aris logo, fall back to committed version
    import shutil

    from rsm.brand_assets import fetch_aris_logo_if_online

    logo_dest = assets_dir / "aris-logo.svg"
    fetched = fetch_aris_logo_if_online(logo_dest)

    if not fetched:
        # Fetch failed, use committed version
        logo_source = Path(__file__).parent / "assets" / "aris-logo-64.svg"
        if logo_source.exists():
            shutil.copy(logo_source, logo_dest)

    if logo_dest.exists():
        print(f"✓ Created {assets_dir}/ with Aris logo")
    else:
        print(f"✓ Created {assets_dir}/")

    # Create custom.css if requested
    if args.css:
        css_file = project_dir / "custom.css"
        css_content = """\
/* Custom CSS for your RSM document */

/* Example: Style a custom paragraph type */
/* .my-custom-type {
    background-color: #f0f0f0;

    border-left: 4px solid #333;
} */
"""
        css_file.write_text(css_content)
        print(f"✓ Created {css_file.name}")

    # Create main RSM file
    rsm_file = project_dir / f"{filename}.rsm"
    rsm_content = f"""\
# {filename.replace("_", " ").replace("-", " ").title()}

:author:{{
  :name: {author}
}} ::


## Introduction

This is your RSM document. Write your content using RSM syntax.


## Basic Formatting

Regular paragraphs are separated by blank lines. You can use *emphasis* and **strong** text.


## Figures

To include a figure:

:figure: {{
  :path: assets/aris-logo.svg
}}
  :caption: Aris logo example.
::


## Math

Inline math: ${{:label: eqn}} x^2 + y^2 = z^2$

Display math:

$$
\\int_0^\\infty e^{{-x^2}} dx = \\frac{{\\sqrt{{\\pi}}}}{{2}}
$$


## Cross-References

To reference from the current file: :ref:eqn::. To cite from the bibliography: :cite:smith2023::.


## Custom Paragraphs

:paragraph: {{:class: note}} This is a custom paragraph with CSS classes.


:references:
@article{{smith2023,
  title={{Example Paper Title}},
  author={{Smith, J.}},
  year={{2026}},
  publisher={{Example Journal}},
  doi={{https://doi.org/10.1201/9780429493638}},
}}
::
"""
    rsm_file.write_text(rsm_content)
    print(f"✓ Created {rsm_file.name}")

    # Create README
    readme_file = project_dir / "README.md"
    readme_content = f"""\
# {filename.replace("_", " ").replace("-", " ").title()}

RSM project initialized by `rsm init`.

## Project Structure

```
.
├── {rsm_file.name}     # Main RSM document
├── assets/           # Place images and other assets here
{"├── custom.css       # Custom CSS styles" if args.css else ""}
└── README.md         # This file
```

## Common Commands

Build the document:
```bash
rsm build {rsm_file.name}
```

Serve with live reload:
```bash
rsm serve {rsm_file.name}
```

Check for errors:
```bash
rsm check {rsm_file.name}
```

Build standalone HTML (no external dependencies):
```bash
rsm build {rsm_file.name} --standalone
```

{"Build with custom CSS:" if args.css else ""}
{"```bash" if args.css else ""}
{f"rsm build {rsm_file.name} --css custom.css" if args.css else ""}
{"```" if args.css else ""}

## Learn More

- RSM Documentation: https://github.com/aris-pub/rsm
- RSM Syntax Guide: https://rsm.readthedocs.io
"""
    readme_file.write_text(readme_content)
    print(f"✓ Created {readme_file.name}")

    print("\n✓ RSM project initialized successfully!")
    print("\nNext steps:")
    print(f"  1. Edit {rsm_file.name}")
    print(f"  2. Run: rsm serve {rsm_file.name}")

    return 0


def _cmd_serve(args: Namespace) -> int:
    """Handle 'rsm serve' subcommand: build the source file, serve it and
    rebuild it each time it or its CSS file is saved."""
    import threading
    import time
    import webbrowser

    # Get the actual working directory (where the user ran the command from)
    # This works even with uv run --project because we capture it immediately
    output_dir = Path.cwd()
    output_filename = None

    if args.output:
        output_dir_str, output_filename = _parse_output_flag(args.output)
        output_dir = Path(output_dir_str)

    # Derive output filename from input if not specified
    if output_filename is None:
        if args.string:
            output_filename = "index.html"
        else:
            input_path = Path(args.src)
            output_filename = f"{input_path.stem}.html"

    # Auto-detect CSS file if not specified via --css flag
    custom_css = args.css
    if custom_css is None and not args.string:
        auto_css_path = Path(args.src).with_suffix(".css")
        if auto_css_path.exists():
            custom_css = str(auto_css_path)

    # sys.argv[0] is the rsm that started serve. A bare "rsm" would run
    # whichever rsm comes first on PATH, which can be another install.
    cmd_parts = [sys.argv[0], "build", args.src]
    if args.string:
        cmd_parts.append("-c")
    if args.output:
        cmd_parts.extend(["-o", args.output])
    if args.standalone:
        cmd_parts.append("--standalone")
    if custom_css:
        cmd_parts.extend(["--css", custom_css])
    if args.menu_right:
        cmd_parts.append("--menu-right")
    if args.sidebar:
        cmd_parts.append("--sidebar")
    if args.no_theme_toggle:
        cmd_parts.append("--no-theme-toggle")
    if args.strict:
        cmd_parts.append("--strict")
    if args.verbose:
        cmd_parts.append("-" + "v" * args.verbose)
    if not args.log_time:
        cmd_parts.append("--log-no-timestamps")
    if not args.log_lineno:
        cmd_parts.append("--log-no-lineno")
    if args.log_format != "rsm":
        cmd_parts.extend(["--log-format", args.log_format])

    # Initial build
    kwargs = {
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
        "write_output": True,
        "standalone": args.standalone,
        "output_dir": str(output_dir),
        "output_filename": output_filename,
        "custom_css": custom_css,
        "theme_toggle": not args.no_theme_toggle,
        "menu_position": "right" if args.menu_right else "left",
        "sidebar": args.sidebar,
        "strict": args.strict,
    }
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src

    app.build(**kwargs)

    # Watch source and CSS files for changes
    server = livereload.Server()
    server.watch(args.src, livereload.shell(cmd_parts))
    if custom_css:
        server.watch(custom_css, livereload.shell(cmd_parts))

    port = args.port
    url = f"http://127.0.0.1:{port}/{output_filename}"

    # Open default browser in a background thread after a short delay
    if not args.no_browser:

        def open_browser() -> None:
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve(
            root=str(output_dir),
            default_filename=output_filename,
            open_url=False,
            port=port,
        )
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port {port} is already in use.")
            print("Please choose a different port using the --port flag:")
            print("  rsm serve <FILE> --port <PORT_NUMBER>")
            print(f"\nFor example: rsm serve {args.src} --port {port + 1}")
            return 1
        raise
    return 0


def main() -> int:
    """Main entry point for rsm CLI with subcommands."""
    parser = ArgumentParser(
        prog="rsm",
        description="Readable Science Markup (RSM) markup language toolchain",
    )
    parser.add_argument(
        "-V",
        "--version",
        help="show rsm-lang version",
        action="version",
        version=f"rsm-lang v{version('rsm-lang')}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="available subcommands",
        required=True,
    )

    # Init subcommand
    init_parser = subparsers.add_parser(
        "init",
        help="initialize a new RSM project",
    )
    init_parser.add_argument(
        "--css",
        help="create a custom.css file",
        action="store_true",
    )
    init_parser.add_argument(
        "--force",
        help="initialize even if RSM files already exist",
        action="store_true",
    )
    init_parser.set_defaults(func=_cmd_init)

    # Build subcommand
    build_parser = subparsers.add_parser(
        "build",
        help="build RSM source to HTML with assets",
    )
    _add_common_args(build_parser, page_style=True)
    build_parser.add_argument(
        "--standalone",
        help="output single self-contained HTML file",
        action="store_true",
    )
    build_parser.add_argument(
        "-o",
        "--output",
        help="output path and/or filename",
        type=str,
        default=None,
    )
    build_parser.add_argument(
        "--no-theme-toggle",
        help="do not apply the reader's saved reading settings (theme, typeface, size) before the page is drawn",
        action="store_true",
    )
    build_parser.add_argument(
        "--sidebar",
        help="add the reader sidebar (contents, notation, proofs, pinned, reading)",
        action="store_true",
    )
    build_parser.set_defaults(func=_cmd_build)

    # Render subcommand
    render_parser = subparsers.add_parser(
        "render",
        help="render RSM source to HTML (stdout only)",
    )
    _add_common_args(render_parser, handrails=True)
    render_parser.add_argument(
        "-s",
        "--silent",
        help="do not show output, only the logs",
        action="store_true",
    )
    render_parser.add_argument(
        "--sidebar",
        help="add the reader sidebar (contents, notation, proofs, pinned, reading)",
        action="store_true",
    )
    render_parser.set_defaults(func=_cmd_render)

    # Check subcommand
    check_parser = subparsers.add_parser(
        "check",
        help="check RSM source for errors",
    )
    _add_common_args(check_parser, verbose=False, strict=False)
    check_parser.set_defaults(log_format="lint", func=_cmd_check)

    # Parse subcommand
    parse_parser = subparsers.add_parser(
        "parse",
        help="parse RSM source and output AST as JSON",
    )
    _add_common_args(parse_parser)
    parse_parser.add_argument(
        "--pretty",
        help="pretty-print JSON output with indentation",
        action="store_true",
    )
    parse_parser.set_defaults(func=_cmd_parse)

    # Export subcommand
    export_parser = subparsers.add_parser(
        "export",
        help="export RSM source to any pandoc-supported format (LaTeX, PDF, EPUB, DOCX, …)",
    )
    _add_common_args(export_parser)
    export_parser.add_argument(
        "--to",
        help="output format (e.g. latex, pdf, epub, docx)",
        default="latex",
        metavar="FORMAT",
    )
    export_parser.add_argument(
        "-o",
        "--output",
        help="output file path (omit to write to stdout)",
        type=str,
        default=None,
    )
    export_parser.set_defaults(func=_cmd_export)

    # Import subcommand
    import_parser = subparsers.add_parser(
        "import",
        help="import a pandoc-supported file and convert it to RSM source",
    )
    import_parser.add_argument(
        "src",
        help="input file path (or source string with -c)",
    )
    import_group = import_parser.add_argument_group("input control")
    import_group.add_argument(
        "-c",
        "--string",
        help="interpret src as a source string, not a path",
        action="store_true",
    )
    import_group.add_argument(
        "--from",
        dest="frm",
        help="input format (e.g. markdown, latex, docx)",
        default="markdown",
        metavar="FORMAT",
    )
    import_group.add_argument(
        "--main",
        help="main .tex file relative to the project, overrides auto-detection",
        default=None,
    )
    import_out = import_parser.add_argument_group("output control")
    import_out.add_argument(
        "-o",
        "--output",
        help="output .rsm file path (omit to write to stdout)",
        type=str,
        default=None,
    )
    import_log = import_parser.add_argument_group("logging control")
    import_log.add_argument("-v", "--verbose", action="count", default=0)
    import_log.add_argument(
        "--log-no-timestamps", dest="log_time", action="store_false"
    )
    import_log.add_argument("--log-no-lineno", dest="log_lineno", action="store_false")
    import_log.add_argument(
        "--log-format",
        choices=["plain", "rsm", "json", "lint"],
        default="rsm",
    )
    import_parser.set_defaults(func=_cmd_import)

    # Serve subcommand
    serve_parser = subparsers.add_parser(
        "serve",
        help="build an RSM file, serve it and rebuild it on each save",
    )

    serve_parser.add_argument(
        "src",
        help="RSM source file to build and serve (or source string with -c)",
    )

    # Input control
    input_opts = serve_parser.add_argument_group("input control")
    input_opts.add_argument(
        "-c",
        "--string",
        help="interpret src as a source string, not a path",
        action="store_true",
    )

    # Output control
    output_opts = serve_parser.add_argument_group("output control")
    output_opts.add_argument(
        "--css",
        help="path to custom CSS file",
        type=str,
        default=None,
    )
    output_opts.add_argument(
        "--menu-right",
        help="position handrail context menus to the right instead of left",
        action="store_true",
    )
    output_opts.add_argument(
        "--standalone",
        help="output single self-contained HTML file",
        action="store_true",
    )
    output_opts.add_argument(
        "-o",
        "--output",
        help="output path and/or filename",
        type=str,
        default=None,
    )
    output_opts.add_argument(
        "--port",
        help="port number for the development server (default: 5500)",
        type=int,
        default=5500,
    )
    output_opts.add_argument(
        "--no-browser",
        help="do not automatically open browser",
        action="store_true",
    )
    output_opts.add_argument(
        "--sidebar",
        help="add the reader sidebar (contents, notation, proofs, pinned, reading)",
        action="store_true",
    )
    output_opts.add_argument(
        "--no-theme-toggle",
        help="do not apply the reader's saved reading settings (theme, typeface, size) before the page is drawn",
        action="store_true",
    )

    # Logging control
    log_opts = serve_parser.add_argument_group("logging control")
    log_opts.add_argument(
        "-v",
        "--verbose",
        help="verbosity",
        action="count",
        default=0,
    )
    log_opts.add_argument(
        "--log-no-timestamps",
        dest="log_time",
        help="exclude timestamp in logs",
        action="store_false",
    )
    log_opts.add_argument(
        "--log-no-lineno",
        dest="log_lineno",
        help="exclude line numbers in logs",
        action="store_false",
    )
    log_opts.add_argument(
        "--log-format",
        help="format for logs (default: rsm)",
        choices=["plain", "rsm", "json", "lint"],
        default="rsm",
    )
    log_opts.add_argument(
        "--strict",
        help="raise exception on CST errors (halt build on syntax errors)",
        action="store_true",
    )

    serve_parser.set_defaults(func=_cmd_serve)

    args = parser.parse_args()
    status: int = args.func(args)
    return status
