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
        "-s",
        "--silent",
        help="do not show output, only the logs",
        action="store_true",
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


def main(parser: ArgumentParser, func: Callable, args: Namespace | None = None) -> int:
    if args is None:
        args = parser.parse_args()
    kwargs = dict(
        handrails=args.handrails,
        loglevel=app.RSMApp.default_log_level - args.verbose * 10,
        log_format=args.log_format,
        log_time=args.log_time,
        log_lineno=args.log_lineno,
    )
    if args.string:
        kwargs["source"] = args.src
    else:
        kwargs["path"] = args.src
    output = func(**kwargs)
    if not args.silent and output:
        print(output)
    return 0


def render() -> int:
    parser = _init_parser()
    return main(parser, app.render)


def lint() -> int:
    parser = _init_parser()
    parser.set_defaults(log_format="lint")
    parser.set_defaults(silent=True)
    return main(parser, app.lint)


def make() -> int:
    parser = _init_parser()
    parser.add_argument("--serve", help="serve and autoreload", action="store_true")
    parser.set_defaults(handrails=True)
    args = parser.parse_args()

    if args.serve:
        other_args = [a for a in sys.argv if a != "--serve"]
        cmd = " ".join(other_args)
        server = livereload.Server()
        server.watch(args.src, livereload.shell(cmd))
        main(parser, app.make, args)
        server.serve(root=".")
    else:
        main(parser, app.make, args)
    return 0
