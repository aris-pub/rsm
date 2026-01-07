"""Input: Path to .rsm file -- Output: file contents.

Locate a file in disk and read its contents.

"""

import logging
from pathlib import Path

logger = logging.getLogger("RSM").getChild("read ")


class Reader:
    """Read the contents of a RSM source file."""

    def __init__(self) -> None:
        self.path: Path = Path()
        """The path of the RSM source file."""

        self.src: str = ""
        """The contents of the RSM source file."""

    def read(self, path: Path | None) -> str:
        """Read the contents of the path.

        Parameters
        ----------
        path
            Location of the RSM file.

        Returns
        -------
        src
            Contents of the file.

        Notes
        -----
        *path* is stored as :attr:`~Reader.path` and *src* is stored as :attr:`~Reader.src`.

        """
        logger.info("Reading...")
        if not path:
            raise TypeError("Expected path, got None")
        self.path = Path(path)
        with open(path) as file:
            self.src = file.read()
        return self.src
