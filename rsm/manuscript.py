"""
manuscript.py
-------------

Classes that represent the manuscript at different stages.

"""

from pathlib import Path


class WebManuscript:
    """In-memory representation of a built manuscript's file tree.

    Stores file contents as a dict mapping virtual paths to text content,
    replacing the previous pyfilesystem2 MountFS dependency.
    """

    def __init__(self, src: Path = None) -> None:
        self.src = Path(src) if src else None
        self.body: str = ""
        self.html: str = ""
        self._files: dict[str, str] = {}
        self._dirs: set[str] = set()

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}(src='{self.src}')"

    def makedir(self, path: str) -> None:
        self._dirs.add(path)

    def writetext(self, path: str, contents: str) -> None:
        self._files[path] = contents

    def readtext(self, path: str) -> str:
        return self._files[path]

    def exists(self, path: str) -> bool:
        return path in self._files or path in self._dirs

    def listdir(self, path: str) -> list[str]:
        prefix = "" if path in ("", ".", "/") else path.rstrip("/") + "/"
        seen = set()
        for p in self._files:
            if not p.startswith(prefix):
                continue
            rest = p[len(prefix):]
            top = rest.split("/", 1)[0]
            if top:
                seen.add(top)
        return sorted(seen)

    def items(self) -> list[tuple[str, str]]:
        return list(self._files.items())
