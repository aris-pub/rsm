"""A program that uses RSM can add its own handler to the "RSM" logger.

RSM sets up its own handler for each run, and must leave the program's
handlers in place.
"""

import logging

import rsm


class _Collect(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def test_a_handler_on_the_rsm_logger_gets_the_warnings():
    handler = _Collect()
    logger = logging.getLogger("RSM")
    logger.addHandler(handler)
    try:
        rsm.render("# T\n\nSee :ref:nope::.\n")
        rsm.render("# T\n\nSee :ref:other::.\n")
    finally:
        logger.removeHandler(handler)
    assert any('"nope"' in m for m in handler.messages), handler.messages
    assert any('"other"' in m for m in handler.messages), handler.messages


def test_rsm_does_not_pile_up_its_own_handlers():
    for _ in range(3):
        rsm.render("# T\n\nText.\n")
    own = [h for h in logging.getLogger("RSM").handlers if type(h) is logging.StreamHandler]
    assert len(own) == 1, own
