"""Configure the logging module for RSM apps."""

import logging
from logging.handlers import BufferingHandler
from typing import Any

import ujson as json

# Shorten level names for nicer output
logging.addLevelName(logging.DEBUG, "DBG")
logging.addLevelName(logging.INFO, "INF")
logging.addLevelName(logging.WARN, "WRN")
logging.addLevelName(logging.ERROR, "ERROR")
logging.addLevelName(logging.CRITICAL, "CRITICAL")

# # Use a log record factory that understands a few extra attributes
# # fmt: off
# old_factory = logging.getLogRecordFactory()
# def rsm_record_factory(*args, **kwargs):
#     record = old_factory(*args, **kwargs)
#     if not hasattr(record, "start_point"):
#         record.start_point = None
#     if not hasattr(record, "end_point"):
#         record.end_point = None
#     return record
# logging.setLogRecordFactory(rsm_record_factory)
# # fmt: on


# Official documentation recommends that library code does not setup logging - it is the
# responsibility of client application code.
# https://docs.python.org/3/howto/logging-cookbook.html#adding-handlers-other-than-nullhandler-to-a-logger-in-a-library
logger = logging.getLogger("RSM")
logger.addHandler(logging.NullHandler())


# The rest of this module defines classes and functions that are meant to be used by
# client application code.
class RSMFormatter(logging.Formatter):
    """Default logging formatter for RSM apps."""

    grey = "\x1b[37;2m"
    blue = "\x1b[34;1m"
    white = "\x1b[37;10m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    boldred = "\x1b[31;1m"
    reset = "\x1b[0m"
    time = grey + "%(asctime)s " + reset
    name = blue + "%(name)s " + reset
    msgformat = "%(levelname)-3s | %(message)s" + reset
    point = " | (%(start_row)d, %(start_col)d) - (%(end_row)d, %(end_col)d) | " + reset
    suffix = grey + " (%(filename)s:%(lineno)d)" + reset

    COLORS = {
        logging.DEBUG: grey,
        logging.INFO: white,
        logging.WARN: yellow,
        logging.ERROR: red,
        logging.CRITICAL: boldred,
    }

    def __init__(
        self, log_time: bool = True, log_lineno: bool = True, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.log_time = log_time
        self.log_lineno = log_lineno

    def format(self, record: logging.LogRecord) -> str:
        fmt = (
            (self.time if self.log_time else "")
            + self.name
            + self.COLORS.get(record.levelno, self.grey)
            + self.msgformat
            + (self.point if hasattr(record, "start_row") else "")
            + self.suffix
        )
        formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


class JSONFormatter(logging.Formatter):
    def __init__(
        self, log_time: bool = True, log_lineno: bool = True, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.log_time = log_time
        self.log_lineno = log_lineno

    def format(self, record: logging.LogRecord) -> str:
        output: dict[str, Any] = {
            "name": record.name,
            "level": record.levelname,
            "msg": record.getMessage(),
            "filename": record.filename,
        }
        if self.log_lineno:
            output["lineno"] = record.lineno
        if self.log_time:
            output["time"] = self.formatTime(record, self.datefmt)
        return json.dumps(output)


class LintFormatter:
    fmt_with_point = "src:%(start_row)d:%(start_col)d: %(levelname)s: %(message)s"
    fmt_sans_point = "src:1:1: %(levelname)s: %(message)s"

    def __init__(
        self, log_time: bool = True, log_lineno: bool = True, *args: Any, **kwargs: Any
    ) -> None:
        self._formatter_with_point = logging.Formatter(
            self.fmt_with_point, *args, **kwargs
        )
        self._formatter_sans_point = logging.Formatter(
            self.fmt_sans_point, *args, **kwargs
        )
        self.log_time = log_time

    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, "start_row"):
            return self._formatter_with_point.format(record)
        else:
            return self._formatter_sans_point.format(record)


class GatherHandler(BufferingHandler):
    def __init__(
        self, levels: list[int], target: logging.Handler | None = None
    ) -> None:
        super().__init__(capacity=1000000)
        self.gatherlevels = set(levels)
        self.buffer = []
        self.target = target

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno in self.gatherlevels:
            self.buffer.append(record)

    def flush(self) -> None:
        self.acquire()
        try:
            if self.target:
                for record in self.buffer:
                    self.target.handle(record)
                self.buffer.clear()
        finally:
            self.release()


def config_rsm_logger(
    level: int = logging.WARNING,
    fmt: str = "rsm",
    log_time: bool = True,
    log_lineno: bool = True,
) -> None:
    """Configure logging for RSM applications.

    By default, the RSM libray creates a logger instance with name "RSM" but it does not
    add any handlers or formatters to it.  Instead, it is the responsibility of client
    application code to setup logging.  This function configures the "RSM" logger in the
    way recommended by library author.  In particular, scripts such as rsm-make and
    rsm-lint use this configuration.

    """
    logging.getLogger("RSM").handlers.clear()
    _config_rsm_logger(fmt, log_time, log_lineno)
    _set_level(level)


def _config_rsm_logger(
    fmt: str = "rsm", log_time: bool = True, log_lineno: bool = True
) -> None:
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARN)
    formatter = {
        "json": JSONFormatter,
        "rsm": RSMFormatter,
        "lint": LintFormatter,
        "plain": lambda *args, **kwargs: logging.Formatter(),
    }[fmt]
    handler.setFormatter(formatter(log_time, log_lineno))
    logger.addHandler(handler)


def _set_level(level: int) -> None:
    level = max(level, logging.DEBUG)
    logger.setLevel(level)
    for h in logger.handlers:
        if h.level > level:
            h.setLevel(level)
