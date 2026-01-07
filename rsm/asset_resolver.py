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
from typing import Protocol

logger = logging.getLogger("RSM").getChild("asset")


class AssetResolver(Protocol):
    """Protocol for resolving asset content from various sources.

    This protocol allows RSM to obtain asset content without being coupled to
    any specific storage mechanism (filesystem, database, remote storage, etc.).
    """

    def resolve_asset(self, path: str) -> str | None:
        """Resolve an asset path to its content.

        Parameters
        ----------
        path
            The asset path/identifier to resolve.

        Returns
        -------
        Optional[str]
            The asset content as a string, or None if the asset cannot be found
            or read.
        """
        ...


class AssetResolverFromDisk:
    """Default asset resolver that reads assets from the filesystem.

    This implementation preserves the existing RSM behavior of reading assets
    directly from disk.
    """

    def resolve_asset(self, path: str) -> str | None:
        """Read asset content from filesystem.

        Parameters
        ----------
        path
            Filesystem path to the asset file.

        Returns
        -------
        Optional[str]
            File content as UTF-8 string, or None if file not found or cannot
            be read as text.
        """
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Asset file not found: {path}")
            return None
        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Error reading asset file {path}: {e}")
            return None
