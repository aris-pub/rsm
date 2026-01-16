# Brand Asset Management

This document explains how RSM manages brand assets (logos, favicons) and the rationale behind the current approach.

## The Problem

RSM uses brand assets from a centralized [brand repository](https://github.com/leotrs/brand) shared across the Aris ecosystem. We need to balance two competing requirements:

1. **Always up-to-date**: When brand assets change in the central repository, RSM should automatically use the latest versions without manual intervention
2. **Reliable offline builds**: Documentation builds and CLI commands should work reliably without internet connectivity

## Rejected Approaches

### Git Submodules
**What we tried**: Adding the brand repository as a git submodule and using symlinks to reference assets.

**Why it didn't work**:
- Requires `git clone --recursive` or manual submodule initialization
- Symlinks break on Windows without admin privileges
- Easy to forget to update the submodule when pulling changes
- Adds complexity for contributors and CI/CD pipelines
- Manual coordination required to update assets across multiple repositories

### Package Distribution (npm/PyPI)
**Why we rejected it**:
- npm package would require Node.js for Python documentation builds
- Creates ecosystem mismatch (Python project depending on Node tooling)
- Still requires manual package updates to get latest assets
- More overhead than the value provided for a few static SVG files

### Always-Fetch from GitHub
**Why we rejected it**:
- Breaks offline work (planes, trains, poor connections)
- Documentation builds fail if GitHub is unavailable
- Slower build times from network requests
- Makes historical builds non-reproducible

### Manual Update Scripts
**Why we rejected it**:
- Requires developers to remember to run update commands
- Most manual approach of all options considered
- Easy to forget, leading to stale assets

## Current Solution: Fetch-with-Fallback

We commit baseline brand assets to this repository and attempt to update them from GitHub on every build, falling back silently if the fetch fails.

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

### Benefits

✅ **Zero developer mental overhead**: No special commands to remember, no submodule updates
✅ **Always up-to-date when online**: Automatically fetches latest assets from GitHub
✅ **Reliable offline builds**: Falls back to committed versions without errors
✅ **Transparent**: Developers don't need to know this system exists
✅ **No symlinks**: Works on all platforms without special permissions
✅ **No submodules**: Standard git workflow, no `--recursive` needed

### Tradeoffs

⚠️ **Network dependency for latest assets**: Must be online to get updates (acceptable for non-critical assets)
⚠️ **Slight build overhead**: Two HTTP requests per doc build when online
⚠️ **Asset duplication**: Committed copies in this repo + central brand repo (acceptable for 3 small SVG files)

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

You only need to do this if you want to update the fallback versions that are used when offline.

## Future Considerations

If brand assets start changing frequently or become large binary files, we may want to revisit this approach. For now, the simplicity and transparency of fetch-with-fallback outweighs the minor network dependency.
