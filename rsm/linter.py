"""
linter.py
---------

RSM Linter: analyze the manuscript tree and log linting messages.

"""

import logging

from . import nodes
from .tsparser import _user_position

logger = logging.getLogger("RSM")


class Linter:
    LINT_LVL = 25

    def __init__(self) -> None:
        logging.LINT = self.LINT_LVL  # type: ignore
        logging.addLevelName(self.LINT_LVL, "LINT")
        logger.lint = lambda msg, *args, **kwargs: logger.log(  # type: ignore
            self.LINT_LVL, msg, *args, **kwargs
        )
        if logger.level > self.LINT_LVL:
            logger.level = self.LINT_LVL

    def lint(self, tree: nodes.Manuscript) -> nodes.Manuscript:
        """Lint the manuscript."""
        logger.info("Linting...")
        self.tree: nodes.Manuscript = tree

        self.lint_manuscript_title()
        self.lint_section_label()
        self.lint_mathblock_inside_paragraph()

        return self.tree

    def _extra(self, node: nodes.Node) -> dict:
        """Make the extra arguments for the logger.lint call."""
        return _user_position(node.start_point, node.end_point)

    def lint_manuscript_title(self) -> None:
        """Manuscript should have a title."""
        if not self.tree.title:
            logger.lint(  # type: ignore[attr-defined]  # added in __init__
                "Manuscript with no title", extra=self._extra(self.tree)
            )

    def lint_section_label(self) -> None:
        """Sections should be labeled."""
        for section in self.tree.traverse(nodeclass=nodes.Section):
            if not section.label:
                logger.lint(  # type: ignore[attr-defined]  # added in __init__
                    "Section with no label", extra=self._extra(section)
                )

    def lint_mathblock_inside_paragraph(self) -> None:
        for block in self.tree.traverse(nodeclass=nodes.MathBlock):
            if not isinstance(block.parent, nodes.Paragraph):
                cls = type(block.parent)
                logger.lint(  # type: ignore[attr-defined]  # added in __init__
                    f"MathBlock must be direct child of Paragraph, not {cls}",
                    extra=self._extra(block),
                )
