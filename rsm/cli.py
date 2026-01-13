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


def _init_parser() -> ArgumentParser:
    parser = ArgumentParser()
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
    parser.add_argument(
        "-V",
        "--version",
        help="rsm-markup version",
        action="version",
        version=f"rsm-markup v{version('rsm-markup')}",
    )

    return parser


def main(parser: ArgumentParser, func: Callable, args: Namespace | None = None, print_output: bool = True) -> int:
    if args is None:
        args = parser.parse_args()
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


def render() -> int:
    parser = _init_parser()
    parser.add_argument(
        "-s",
        "--silent",
        help="do not show output, only the logs",
        action="store_true",
    )
    args = parser.parse_args()
    return main(parser, app.render, args=args, print_output=not args.silent)


def lint() -> int:
    parser = _init_parser()
    parser.set_defaults(log_format="lint")
    return main(parser, app.lint, print_output=False)


def _parse_output_flag(value: str) -> tuple[str, str]:
    """Parse -o flag into (output_dir, output_filename).

    Cases:
    - "myfile" -> (".", "myfile.html")
    - "build/" -> ("build", "index.html")
    - "build/myfile" -> ("build", "myfile.html")
    """
    if "/" not in value:
        # Case 1: no slash, it's a filename
        return (".", f"{value}.html")
    elif value.endswith("/"):
        # Case 2: ends with slash, it's a directory
        return (value.rstrip("/"), "index.html")
    else:
        # Case 3: contains slash but doesn't end with it
        # Split at rightmost slash
        parts = value.rsplit("/", 1)
        return (parts[0], f"{parts[1]}.html")


def make() -> int:
    parser = _init_parser()
    parser.add_argument("--serve", help="serve and autoreload", action="store_true")
    parser.add_argument("--standalone", help="output single self-contained HTML file", action="store_true")
    parser.add_argument("-o", "--output", help="output path and/or filename", type=str, default=None)
    parser.add_argument("-p", "--print", help="print HTML to stdout", action="store_true", dest="print_output")
    parser.set_defaults(handrails=True)
    args = parser.parse_args()

    # Parse output directory and filename
    output_dir = "."
    output_filename = "index.html"
    if args.output:
        output_dir, output_filename = _parse_output_flag(args.output)

    # Build kwargs for app.make with write_output=True for CLI
    kwargs = {
        "handrails": args.handrails,
        "loglevel": app.RSMApp.default_log_level - args.verbose * 10,
        "log_format": args.log_format,
        "log_time": args.log_time,
        "log_lineno": args.log_lineno,
        "write_output": True,  # CLI always writes files
        "standalone": args.standalone,
        "output_dir": output_dir,
        "output_filename": output_filename,
        "custom_css": args.css,
    }
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src

    if args.serve:
        other_args = [a for a in sys.argv if a != "--serve"]
        cmd = " ".join(other_args)
        server = livereload.Server()
        server.watch(args.src, livereload.shell(cmd))
        output = app.make(**kwargs)
        if args.print_output and output:
            print(output)
        server.serve(root=".")
    else:
        output = app.make(**kwargs)
        if args.print_output and output:
            print(output)
    return 0
