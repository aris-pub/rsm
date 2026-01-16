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


def _add_common_args(parser: ArgumentParser) -> None:
    """Add common arguments shared by all subcommands."""
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
    output_opts.add_argument(
        "-r",
        "--handrails",
        help="output handrails",
        action="store_true",
    )
    output_opts.add_argument(
        "--css",
        help="path to custom CSS file",
        type=str,
        default=None,
    )

    log_opts = parser.add_argument_group("logging control")
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


def _run_app(func: Callable, args: Namespace, print_output: bool = True) -> int:
    """Run an RSM app function with parsed arguments."""
    kwargs = {
        "handrails": args.handrails,
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
    }
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src
    output = func(**kwargs)
    if print_output and output:
        print(output)
    return 0


def _cmd_render(args: Namespace) -> int:
    """Handle 'rsm render' subcommand."""
    return _run_app(app.render, args, print_output=not args.silent)


def _cmd_check(args: Namespace) -> int:
    """Handle 'rsm check' subcommand."""
    return _run_app(app.lint, args, print_output=False)


def _parse_output_flag(value: str) -> tuple[str, str]:
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
        auto_css_path = input_path.with_suffix('.css')
        if auto_css_path.exists():
            custom_css = str(auto_css_path)

    kwargs = {
        "handrails": args.handrails,
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
        "write_output": True,
        "standalone": args.standalone,
        "output_dir": output_dir,
        "output_filename": output_filename,
        "custom_css": custom_css,
    }
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src

    output = app.build(**kwargs)
    if args.print_output and output:
        print(output)
    return 0


def _find_html_files(directory: str) -> list:
    """Find all HTML files in the given directory (non-recursive).

    Excludes the special .rsm-index.html file used for directory listings.

    Parameters
    ----------
    directory : str
        Path to directory to search

    Returns
    -------
    list of Path
        List of HTML file paths, sorted alphabetically
    """
    dir_path = Path(directory)
    html_files = []

    for file_path in dir_path.glob("*.html"):
        if file_path.is_file() and file_path.name != ".rsm-index.html":
            html_files.append(file_path)

    return sorted(html_files, key=lambda p: p.name)


def _generate_index_page(html_files: list) -> str:
    """Generate an HTML index page listing all HTML files.

    Parameters
    ----------
    html_files : list of Path
        List of HTML file paths to include in the listing

    Returns
    -------
    str
        HTML content for the index page
    """
    sorted_files = sorted(html_files, key=lambda p: p.name)

    links = []
    for file_path in sorted_files:
        filename = file_path.name
        links.append(f'        <li><a href="{filename}">{filename}</a></li>')

    links_html = "\n".join(links)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSM - Available Pages</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.5rem;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        li {{
            margin: 0.75rem 0;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
            font-size: 1.1rem;
            padding: 0.5rem;
            display: block;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}
        a:hover {{
            background-color: #f0f0f0;
        }}
        .info {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <h1>Available Pages</h1>
    <ul>
{links_html}
    </ul>
    <div class="info">
        <p>Serving {len(sorted_files)} HTML file(s) from this directory.</p>
    </div>
</body>
</html>"""

    return html




def _cmd_init(args: Namespace) -> int:
    """Handle 'rsm init' subcommand - scaffold a new RSM project."""
    import sys
    from pathlib import Path

    # Get current directory
    project_dir = Path.cwd()

    # Check if directory already has RSM files
    existing_rsm = list(project_dir.glob("*.rsm"))
    if existing_rsm and not args.force:
        print(f"Error: Directory already contains RSM files: {', '.join(f.name for f in existing_rsm)}")
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
    from rsm.brand_assets import fetch_aris_logo_if_online
    import shutil

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
# {filename.replace('_', ' ').replace('-', ' ').title()}

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

:paragraph: {{:types: note}} This is a custom paragraph with `types` meta key.


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
# {filename.replace('_', ' ').replace('-', ' ').title()}

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

    print(f"\n✓ RSM project initialized successfully!")
    print(f"\nNext steps:")
    print(f"  1. Edit {rsm_file.name}")
    print(f"  2. Run: rsm serve {rsm_file.name}")

    return 0


def _cmd_serve(args: Namespace) -> int:
    """Handle 'rsm serve' subcommand.

    Two modes:
    1. With src: Build the source file first, then serve with auto-rebuild
    2. Without src: Just serve existing HTML files in current directory
    """
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

    # Mode 1: Build from source if provided
    if args.src:
        # Derive output filename from input if not specified
        if output_filename is None:
            if args.string:
                output_filename = "index.html"
            else:
                input_path = Path(args.src)
                output_filename = f"{input_path.stem}.html"
        # Reconstruct the build command for livereload
        cmd_parts = ["rsm", "build", args.src]
        if args.string:
            cmd_parts.append("-c")
        if args.output:
            cmd_parts.extend(["-o", args.output])
        if args.standalone:
            cmd_parts.append("--standalone")
        if args.css:
            cmd_parts.extend(["--css", args.css])
        if args.verbose:
            cmd_parts.append("-" + "v" * args.verbose)
        if not args.log_time:
            cmd_parts.append("--log-no-timestamps")
        if not args.log_lineno:
            cmd_parts.append("--log-no-lineno")
        if args.log_format != "rsm":
            cmd_parts.extend(["--log-format", args.log_format])

        cmd = " ".join(cmd_parts)

        # Initial build
        kwargs = {
            "handrails": args.handrails,
            "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
            "log_format": args.log_format,
            "log_time": args.log_time,
            "log_lineno": args.log_lineno,
            "write_output": True,
            "standalone": args.standalone,
            "output_dir": str(output_dir),
            "output_filename": output_filename,
            "custom_css": args.css,
        }
        if args.string:
            kwargs["source"] = args.src
        else:
            kwargs["path"] = args.src

        output = app.build(**kwargs)
        if args.print_output and output:
            print(output)

        # Watch source and CSS files for changes
        server = livereload.Server()
        server.watch(args.src, livereload.shell(cmd))
        if args.css:
            server.watch(args.css, livereload.shell(cmd))

    # Mode 2: Serve and watch all .rsm files in directory
    else:
        server = livereload.Server()

        # Find all .rsm files in current directory
        rsm_files = list(output_dir.glob("*.rsm"))

        if rsm_files:
            print(f"Watching {len(rsm_files)} RSM file(s) for changes...")
            for rsm_file in rsm_files:
                print(f"  - {rsm_file.name}")
                # Create build command for this specific file
                output_name = rsm_file.stem  # filename without extension
                build_cmd = f"rsm build {rsm_file} -o {output_name}"
                if args.css:
                    build_cmd += f" --css {args.css}"
                if args.standalone:
                    build_cmd += " --standalone"

                # Add a callback to regenerate index after build
                def rebuild_callback(rsm_path=rsm_file, cmd=build_cmd):
                    # Rebuild the specific file
                    livereload.shell(cmd)()
                    # Regenerate the index page to include any new HTML files
                    html_files = _find_html_files(str(output_dir))
                    if len(html_files) > 1:
                        index_content = _generate_index_page(html_files)
                        index_path = output_dir / ".rsm-index.html"
                        index_path.write_text(index_content)
                    elif len(html_files) == 1:
                        # Remove index if it exists (we're back to single file)
                        index_path = output_dir / ".rsm-index.html"
                        if index_path.exists():
                            index_path.unlink()

                server.watch(str(rsm_file), rebuild_callback)
        else:
            print("No RSM files found in directory")
            print("Watching HTML files for changes (reload only, no rebuild)...")
            # Watch HTML files for reload only
            html_files = _find_html_files(str(output_dir))
            for html_file in html_files:
                server.watch(str(html_file))

        # Also watch CSS if provided
        if args.css:
            # When CSS changes, rebuild all RSM files
            if rsm_files:
                def css_rebuild_callback():
                    # Rebuild all RSM files
                    for rsm_file in rsm_files:
                        output_name = rsm_file.stem
                        cmd = f"rsm build {rsm_file} -o {output_name}"
                        if args.css:
                            cmd += f" --css {args.css}"
                        if args.standalone:
                            cmd += " --standalone"
                        livereload.shell(cmd)()
                    # Regenerate index
                    html_files = _find_html_files(str(output_dir))
                    if len(html_files) > 1:
                        index_content = _generate_index_page(html_files)
                        index_path = output_dir / ".rsm-index.html"
                        index_path.write_text(index_content)
                    elif len(html_files) == 1:
                        # Remove index if it exists
                        index_path = output_dir / ".rsm-index.html"
                        if index_path.exists():
                            index_path.unlink()

                server.watch(args.css, css_rebuild_callback)

    # Determine what file to serve based on HTML files in output directory
    html_files = _find_html_files(str(output_dir))
    default_file = "index.html"

    if len(html_files) == 0:
        # No HTML files found
        if args.src:
            # We just built something, serve it
            default_file = output_filename
        else:
            # Nothing to serve, generate empty index page
            print("Warning: No HTML files found in current directory")
            index_content = _generate_index_page(html_files)
            index_path = output_dir / ".rsm-index.html"
            index_path.write_text(index_content)
            default_file = ".rsm-index.html"
    elif len(html_files) == 1:
        # Single HTML file, serve it directly
        default_file = html_files[0].name
    else:
        # Multiple HTML files, generate an index page
        index_content = _generate_index_page(html_files)
        index_path = output_dir / ".rsm-index.html"
        index_path.write_text(index_content)
        default_file = ".rsm-index.html"

    # Start serving
    # Don't use livereload's open_url - we'll open browser with specific URL
    port = args.port

    # Determine the URL to open
    if len(html_files) == 1:
        # Single file - navigate directly to it
        url = f"http://127.0.0.1:{port}/{default_file}"
    else:
        # Multiple files or no files - show index or root
        url = f"http://127.0.0.1:{port}/{default_file}" if default_file != "index.html" else f"http://127.0.0.1:{port}/"

    # Open default browser in a background thread after a short delay
    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve(root=str(output_dir), default_filename=default_file, open_url=False, port=port)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port {port} is already in use.")
            print(f"Please choose a different port using the --port flag:")
            print(f"  rsm serve --port <PORT_NUMBER>")
            print(f"\nFor example: rsm serve --port {port + 1}")
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
        help="show rsm-markup version",
        action="version",
        version=f"rsm-markup v{version('rsm-markup')}",
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
    _add_common_args(build_parser)
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
        "-p",
        "--print",
        help="print HTML to stdout",
        action="store_true",
        dest="print_output",
    )
    build_parser.set_defaults(handrails=True, func=_cmd_build)

    # Render subcommand
    render_parser = subparsers.add_parser(
        "render",
        help="render RSM source to HTML (stdout only)",
    )
    _add_common_args(render_parser)
    render_parser.add_argument(
        "-s",
        "--silent",
        help="do not show output, only the logs",
        action="store_true",
    )
    render_parser.set_defaults(func=_cmd_render)

    # Check subcommand
    check_parser = subparsers.add_parser(
        "check",
        help="check RSM source for errors",
    )
    _add_common_args(check_parser)
    check_parser.set_defaults(log_format="lint", func=_cmd_check)

    # Serve subcommand
    serve_parser = subparsers.add_parser(
        "serve",
        help="serve HTML files from directory with auto-reload",
    )

    # Optional src argument
    serve_parser.add_argument(
        "src",
        nargs="?",
        help="RSM source file to build before serving (optional)",
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
        "-r",
        "--handrails",
        help="output handrails",
        action="store_true",
    )
    output_opts.add_argument(
        "--css",
        help="path to custom CSS file",
        type=str,
        default=None,
    )
    output_opts.add_argument(
        "--standalone",
        help="output single self-contained HTML file",
        action="store_true",
    )
    output_opts.add_argument(
        "-o",
        "--output",
        help="output path and/or filename (for build)",
        type=str,
        default=None,
    )
    output_opts.add_argument(
        "-p",
        "--print",
        help="print HTML to stdout on each rebuild",
        action="store_true",
        dest="print_output",
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
        help="format for logs",
        choices=["plain", "rsm", "json", "lint"],
        default="rsm",
    )

    serve_parser.set_defaults(handrails=True, func=_cmd_serve)

    args = parser.parse_args()
    return args.func(args)
