"""Asset resolution protocol and implementations for RSM.

This module provides a protocol-based dependency injection system for asset loading,
allowing external callers to provide custom asset loading logic while keeping the
current disk-based behavior as the default.

Technical Debt Note:
This implementation creates an architectural inconsistency where the main RSM source
file is read from disk via the Reader class, but assets are read via the AssetResolver
system. This should be unified in future refactoring to have consistent file access
patterns across the entire RSM package.
"""

import logging
from pathlib import Path
from typing import Protocol

logger = logging.getLogger("RSM").getChild("asset")


class AssetResolver(Protocol):
    """Protocol for resolving asset content from various sources.

    This protocol allows RSM to obtain asset content without being coupled to
    any specific storage mechanism (filesystem, database, remote storage, etc.).
    """

    def resolve_asset(self, path: str) -> str | bytes | None:
        """Resolve an asset path to its content.

        Parameters
        ----------
        path
            The asset path/identifier to resolve.

        Returns
        -------
        str | bytes | None
            Text content as ``str``, binary content (e.g. images) as ``bytes``,
            or None if the asset cannot be found or read.
        """
        ...


class AssetResolverFromDisk:
    """Default asset resolver that reads assets from the filesystem.

    This implementation preserves the existing RSM behavior of reading assets
    directly from disk.
    """

    def resolve_asset(self, path: str) -> str | bytes | None:
        """Read asset content from filesystem.

        Parameters
        ----------
        path
            Filesystem path to the asset file.

        Returns
        -------
        str | bytes | None
            File content decoded as UTF-8 ``str`` for text assets, raw ``bytes``
            for binary assets (e.g. PNG/JPEG images), or None if the file is not
            found or cannot be read. Binary assets are not a read error: callers
            that inline assets (standalone data URIs) need the raw bytes.
        """
        try:
            raw = Path(path).read_bytes()
        except FileNotFoundError:
            logger.error(f"Asset file not found: {path}")
            return None
        except OSError as e:
            logger.error(f"Error reading asset file {path}: {e}")
            return None

        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw
