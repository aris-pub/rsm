"""Regression test for the binary-asset path through `_resolve_image_src`.

A :figure: block with a PNG :path: must not cause the disk asset resolver to
attempt a UTF-8 read on the binary file.  The pipeline used to embed the path
directly into the <img src="..."> attribute; commit ed55dc3 (2026-03-21,
"fix: resolve image assets through asset resolver as data URIs") changed
`_render_image` to call `_resolve_image_src` for every image so that Studio
uploads could be inlined as base64 data URIs.

The disk-based AssetResolverFromDisk reads files in text mode
(``encoding='utf-8'``) and the PNG file signature begins with 0x89, which is
not valid UTF-8.  The resolver therefore raises a UnicodeDecodeError, the
error is logged at ERROR level, and `_resolve_image_src` falls back to the
raw path.  The fallback keeps the rendered HTML correct (so existing
`test_figure.py` cases stay green), but the build emits noise on every PNG
figure.  This test pins down the regression.
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path

import pytest

import rsm


# Smallest valid PNG: 8-byte signature + minimal IHDR/IDAT/IEND chunks.
# Hex-decoded 1×1 transparent PNG.  Source: stock minimal PNG often used in
# test fixtures.
_MINIMAL_PNG = bytes.fromhex(
    "89504E470D0A1A0A0000000D49484452"
    "0000000100000001080600000001"
    "1F15C40000000A49444154789C6300"
    "01000000050001"
    "0D0A2DB400000000"
    "49454E44AE426082"
)


@pytest.fixture
def png_figure_workspace(tmp_path: Path) -> Path:
    """Create a tmp dir containing a 1×1 PNG and a minimal RSM that references it."""
    (tmp_path / "tiny.png").write_bytes(_MINIMAL_PNG)
    (tmp_path / "tiny.rsm").write_text(
        ":figure: {\n  :path: tiny.png\n}\n::\n",
        encoding="utf-8",
    )
    return tmp_path


def test_png_figure_build_emits_no_utf8_decode_error(
    png_figure_workspace: Path,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Building a PNG figure must not produce an ERROR-level
    'utf-8' codec decode log record.

    Before ed55dc3, `_render_image` set `src=node.path` directly and the
    asset resolver never touched the image.  After ed55dc3, every image
    flows through `_resolve_image_src` → `AssetResolverFromDisk.resolve_asset`
    which opens the file with `encoding='utf-8'`.  For any PNG the
    first-byte read fails (0x89 is the PNG signature), the resolver logs
    an ERROR, and the fallback returns the raw path.  The HTML is still
    correct but the build is loud.

    This test fails until the resolver (or the call site) stops attempting
    a UTF-8 read on binary image assets.
    """
    rsm_path = png_figure_workspace / "tiny.rsm"
    output_dir = png_figure_workspace / "out"

    # The asset resolver opens paths relative to cwd; ensure the PNG is
    # found so we exercise the binary-read branch, not the file-not-found
    # branch.
    monkeypatch.chdir(png_figure_workspace)

    caplog.set_level(logging.ERROR, logger="RSM")
    rsm.build(
        path=str(rsm_path),
        write_output=True,
        output_dir=str(output_dir),
        output_filename="tiny.html",
    )

    decode_errors = [
        rec.getMessage()
        for rec in caplog.records
        if rec.levelno >= logging.ERROR
        and "utf-8" in rec.getMessage().lower()
        and "decode" in rec.getMessage().lower()
    ]
    assert decode_errors == [], (
        "Building a PNG figure produced UTF-8 decode errors:\n"
        + "\n".join(f"  - {m}" for m in decode_errors)
    )


def test_png_figure_build_emits_no_unable_to_resolve_warning(
    png_figure_workspace: Path,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Building a PNG figure must not produce 'Unable to resolve required
    asset' warnings for the referenced PNG file.

    Consequence of the same regression: after `_resolve_image_src` fails
    to UTF-8-decode the PNG, `find_required_assets` extracts the same path
    from the body via `src="..."` regex and `mount_required_assets`
    re-runs the same broken text read, emitting a warning per PNG.
    """
    rsm_path = png_figure_workspace / "tiny.rsm"
    output_dir = png_figure_workspace / "out"

    monkeypatch.chdir(png_figure_workspace)

    caplog.set_level(logging.WARNING, logger="RSM")
    rsm.build(
        path=str(rsm_path),
        write_output=True,
        output_dir=str(output_dir),
        output_filename="tiny.html",
    )

    unresolved = [
        rec.getMessage()
        for rec in caplog.records
        if rec.levelno >= logging.WARNING
        and "Unable to resolve required asset" in rec.getMessage()
        and "tiny.png" in rec.getMessage()
    ]
    assert unresolved == [], (
        "Building a PNG figure produced unresolved-asset warnings:\n"
        + "\n".join(f"  - {m}" for m in unresolved)
    )


def test_standalone_png_figure_inlined_as_correct_data_uri(
    png_figure_workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A standalone build must inline an on-disk PNG as a correct base64 data URI.

    This pins the binary-read branch of the disk resolver end to end: the raw
    PNG bytes (not a UTF-8 text read) must be base64-encoded into the <img src>.
    """
    monkeypatch.chdir(png_figure_workspace)

    src = (png_figure_workspace / "tiny.rsm").read_text(encoding="utf-8")
    html = rsm.render(src, standalone=True)

    expected_b64 = base64.b64encode(_MINIMAL_PNG).decode("ascii")
    assert f"data:image/png;base64,{expected_b64}" in html
    assert 'src="tiny.png"' not in html
