"""A :video: must fit its box at any viewport width (rsm-29p).

The fixture is a real 640x360 WebM. Without a max-width rule the <video> kept
its intrinsic 640px width inside a ~280px content box at a 375px viewport, so
the figure scrolled sideways and axe flagged scrollable-region-focusable.
"""

import shutil
from pathlib import Path

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

FIXTURE = Path(__file__).parent / "fixtures" / "video-640x360.webm"

SRC = """# Video

:video: {
  :path: video-640x360.webm
}
:caption: A gray clip.
::
"""


@pytest.fixture
def video_page(tmp_path):
    shutil.copy(FIXTURE, tmp_path / FIXTURE.name)
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "video.html"
    out.write_text(html)
    return out.as_uri()


@pytest.mark.parametrize("width", [375, 1280])
def test_video_fits_its_box(page: Page, video_page: str, width: int):
    page.set_viewport_size({"width": width, "height": 800})
    page.goto(video_page, wait_until="load")
    # A real file, so the layout uses the true intrinsic size, not the 300x150
    # placeholder a missing source would give.
    page.wait_for_function(
        "() => document.querySelector('figure.video video').readyState >= 1",
        timeout=10_000,
    )

    m = page.evaluate(
        """() => {
          const v = document.querySelector('figure.video video');
          const box = v.parentElement.getBoundingClientRect();
          const r = v.getBoundingClientRect();
          const fig = v.closest('figure');
          return {
            natW: v.videoWidth, natH: v.videoHeight,
            w: r.width, h: r.height, boxW: box.width,
            figOverflow: fig.scrollWidth - fig.clientWidth,
            pageOverflow: document.documentElement.scrollWidth - window.innerWidth,
          };
        }"""
    )

    assert (m["natW"], m["natH"]) == (640, 360)
    assert m["w"] <= m["boxW"] + 0.5, f"video {m['w']}px wider than its {m['boxW']}px box"
    assert m["figOverflow"] <= 0, f"figure scrolls sideways by {m['figOverflow']}px"
    assert m["pageOverflow"] <= 1, f"page scrolls sideways by {m['pageOverflow']}px"
    assert abs(m["w"] / m["h"] - 640 / 360) < 0.02, f"aspect ratio lost: {m['w']}x{m['h']}"
