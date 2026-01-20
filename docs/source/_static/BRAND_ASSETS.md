# Brand Asset Management

This document explains how RSM manages brand assets (logos, favicons) and the rationale
behind the current approach.

## The Problem

RSM uses brand assets from a centralized [brand
repository](https://github.com/leotrs/brand) shared across the Aris ecosystem. We need
to balance two competing requirements:

1. **Always up-to-date**: When brand assets change in the central repository, RSM should
   automatically use the latest versions without manual intervention
2. **Reliable offline builds**: Documentation builds and CLI commands should work
   reliably without internet connectivity

## Rejected Approaches

### Git Submodules
**Why we rejected it**: Requires `git clone --recursive` or manual submodule
initialization. Requires symlink for sphinx to work, adds complexity.

### Package Distribution (npm/PyPI)
**Why we rejected it**: npm package would require Node.js for Python documentation
builds

### Always-Fetch from GitHub
**Why we rejected it**: Breaks offline work (planes, trains, poor connections)

### Manual Update Scripts
**Why we rejected it**: Requires developers to remember to run update commands

## Current Solution: Fetch-with-Fallback
We commit baseline brand assets to this repository and attempt to update them from
GitHub on every build, falling back silently if the fetch fails.

### How It Works

**For Sphinx Documentation** (`docs/source/conf.py`):
```python
from rsm.brand_assets import update_brand_assets_if_online

static_dir = Path(__file__).parent / "_static"
update_brand_assets_if_online(static_dir)
```

On every documentation build:
1. Try to fetch latest `logo.svg` and `favicon.ico` from GitHub
2. If successful, overwrite the committed versions in `_static/`
3. If fetch fails (offline/error), silently use the existing committed versions
4. Sphinx then uses whichever version is in `_static/`

**For CLI Init Command** (`rsm init`):
```python
from rsm.brand_assets import fetch_aris_logo_if_online

fetched = fetch_aris_logo_if_online(logo_dest)
if not fetched:
    # Fall back to committed version in rsm/assets/
    shutil.copy(logo_source, logo_dest)
```

When creating a new project:
1. Try to fetch latest `aris-logo-64.svg` from GitHub
2. If successful, copy the fetched version to `assets/`
3. If fetch fails, copy the committed version from `rsm/assets/`

## Asset Locations

**Committed baseline assets**:
- `docs/source/_static/logo.svg` - RSM logo for documentation
- `docs/source/_static/favicon.ico` - RSM favicon for documentation
- `rsm/assets/aris-logo-64.svg` - Aris logo for `rsm init` command

**Fetch source** (when online):
- https://raw.githubusercontent.com/leotrs/brand/main/logos/rsm/logo.svg
- https://raw.githubusercontent.com/leotrs/brand/main/logos/rsm/favicon.ico
- https://raw.githubusercontent.com/leotrs/brand/main/logos/aris/aris-logo-64.svg

## For Developers

**Normal workflow**: No action needed. Build docs or run `rsm init` as usual.

**Updating committed assets manually** (if needed):
```bash
# Fetch latest and commit them as new baseline
curl -o docs/source/_static/logo.svg \
  https://raw.githubusercontent.com/leotrs/brand/main/logos/rsm/logo.svg
curl -o docs/source/_static/favicon.ico \
  https://raw.githubusercontent.com/leotrs/brand/main/logos/rsm/favicon.ico
curl -o rsm/assets/aris-logo-64.svg \
  https://raw.githubusercontent.com/leotrs/brand/main/logos/aris/aris-logo-64.svg
git add docs/source/_static/*.{svg,ico} rsm/assets/aris-logo-64.svg
git commit -m "Update baseline brand assets"
```

You only need to do this if you want to update the fallback versions that are used when
offline.

## Future Considerations

If brand assets start changing frequently or become large binary files, we may want to
revisit this approach. For now, the simplicity and transparency of fetch-with-fallback
outweighs the minor network dependency.
