"""RSM command line utilities.

The apps implemented in :mod:`rsm.app` are hereby exposed to the user as command line
utilities.

"""

import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Callable
from importlib.metadata import version

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
    - "build/" -> ("build", "index.html")
    - "build/myfile" -> ("build", "myfile.html")
    """
    if "/" not in value:
        return (".", f"{value}.html")
    elif value.endswith("/"):
        return (value.rstrip("/"), "index.html")
    else:
        parts = value.rsplit("/", 1)
        return (parts[0], f"{parts[1]}.html")


def _cmd_build(args: Namespace) -> int:
    """Handle 'rsm build' subcommand."""
    output_dir = "."
    output_filename = "index.html"
    if args.output:
        output_dir, output_filename = _parse_output_flag(args.output)

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
        "custom_css": args.css,
    }
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src

    output = app.build(**kwargs)
    if args.print_output and output:
        print(output)
    return 0


def _cmd_serve(args: Namespace) -> int:
    """Handle 'rsm serve' subcommand."""
    output_dir = "."
    output_filename = "index.html"
    if args.output:
        output_dir, output_filename = _parse_output_flag(args.output)

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
        "output_dir": output_dir,
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

    # Start livereload server
    server = livereload.Server()
    server.watch(args.src, livereload.shell(cmd))
    if args.css:
        server.watch(args.css, livereload.shell(cmd))
    server.serve(root=".")
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
        help="build and serve with auto-reload",
    )
    _add_common_args(serve_parser)
    serve_parser.add_argument(
        "--standalone",
        help="output single self-contained HTML file",
        action="store_true",
    )
    serve_parser.add_argument(
        "-o",
        "--output",
        help="output path and/or filename",
        type=str,
        default=None,
    )
    serve_parser.add_argument(
        "-p",
        "--print",
        help="print HTML to stdout on each rebuild",
        action="store_true",
        dest="print_output",
    )
    serve_parser.set_defaults(handrails=True, func=_cmd_serve)

    args = parser.parse_args()
    return args.func(args)
