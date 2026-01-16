"""Brand asset fetching with fallback to committed versions.

This module provides transparent, always-up-to-date brand assets while
maintaining offline build capability. See docs/source/_static/BRAND_ASSETS.md
for the full rationale.
"""

import urllib.request
from pathlib import Path


BRAND_BASE_URL = "https://raw.githubusercontent.com/leotrs/brand/main/logos"


def update_brand_assets_if_online(static_dir: Path) -> None:
    """
    Try to fetch latest brand assets from GitHub.

    Falls back to committed versions if offline or fetch fails.
    This function is called by Sphinx conf.py on every build.

    Parameters
    ----------
    static_dir : Path
        The _static directory where assets should be placed.
    """
    assets = {
        "logo.svg": f"{BRAND_BASE_URL}/rsm/logo.svg",
        "favicon.ico": f"{BRAND_BASE_URL}/rsm/favicon.ico",
    }

    for filename, url in assets.items():
        dest = static_dir / filename
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception:
            # Network unavailable or fetch failed
            # Silently fall back to committed version
            pass


def fetch_aris_logo_if_online(dest_path: Path) -> bool:
    """
    Try to fetch latest Aris logo from GitHub.

    This function is called by the CLI init command to get the latest
    Aris logo for new projects.

    Parameters
    ----------
    dest_path : Path
        Where to save the fetched logo.

    Returns
    -------
    bool
        True if fetch succeeded, False if it failed (offline/error).
    """
    url = f"{BRAND_BASE_URL}/aris/aris-logo-64.svg"

    try:
        urllib.request.urlretrieve(url, dest_path)
        return True
    except Exception:
        return False
