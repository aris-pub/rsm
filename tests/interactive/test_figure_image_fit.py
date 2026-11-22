"""An image in a :figure: that is wider than the text column shrinks to the column
and keeps its aspect ratio, as a video does (rsm-cj3). Before, it kept its
natural pixel width and scrolled sideways inside the figure, cut off."""

import struct
import zlib

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

WIDE = (920, 460)
NARROW = (200, 100)


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = b"".join(b"\x00" + b"\x80\x80\x80" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


SRC = """# Images

A paragraph that sets the width of the text column.

:figure: {:label: fig-plain, :path: wide.png}

  :caption: A wide image.

::

:figure: {:label: fig-dark, :path: wide.png, :dark: wide-dark.png}

  :caption: A wide image with a dark version.

::

:figure: {:label: fig-narrow, :path: narrow.png}

  :caption: A narrow image.

::

:tabs:

  :tab: {:title: First}

    :figure: {:label: fig-tab, :path: wide.png}

      :caption: A wide image in a tab.

    ::

  ::

::

:theorem: {:label: thm}

  A claim with a figure.

  :figure: {:label: fig-block, :path: wide.png}

    :caption: A wide image in a theorem.

  ::

::
"""


@pytest.fixture
def images_page(tmp_path):
    (tmp_path / "wide.png").write_bytes(_png(*WIDE))
    (tmp_path / "wide-dark.png").write_bytes(_png(*WIDE))
    (tmp_path / "narrow.png").write_bytes(_png(*NARROW))
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "images.html"
    out.write_text(html)
    return out.as_uri()


def _measure(page: Page, label: str) -> dict:
    return page.evaluate(
        """(label) => {
          const fig = document.getElementById(label);
          const img = fig.querySelector('img');
          const r = img.getBoundingClientRect();
          const para = document.querySelector('.manuscript .paragraph');
          // Measured on the image's content zone, not on the figure: inside a
          // block the figure's handrail zones overflow it whatever the image.
          const zone = img.closest('.hr-content-zone');
          const overflow = zone.scrollWidth - zone.clientWidth;
          return {
            natW: img.naturalWidth, natH: img.naturalHeight,
            w: r.width, h: r.height,
            columnW: para.getBoundingClientRect().width,
            overflow,
          };
        }""",
        label,
    )


@pytest.mark.parametrize("label", ["fig-plain", "fig-dark", "fig-tab", "fig-block"])
def test_wide_image_shrinks_to_the_column(page: Page, images_page: str, label: str):
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(images_page, wait_until="load")

    m = _measure(page, label)

    assert (m["natW"], m["natH"]) == WIDE
    assert m["w"] <= m["columnW"] + 0.5, (
        f"image {m['w']}px wider than the {m['columnW']}px column"
    )
    assert m["overflow"] <= 0, f"image scrolls sideways by {m['overflow']}px"
    assert abs(m["w"] / m["h"] - WIDE[0] / WIDE[1]) < 0.02, (
        f"aspect ratio lost: {m['w']}x{m['h']}"
    )


def test_dark_picture_shrinks_in_dark_mode(page: Page, images_page: str):
    page.emulate_media(color_scheme="dark")
    test_wide_image_shrinks_to_the_column(page, images_page, "fig-dark")


def test_narrow_image_keeps_its_natural_size(page: Page, images_page: str):
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(images_page, wait_until="load")

    m = _measure(page, "fig-narrow")

    assert (m["w"], m["h"]) == NARROW
