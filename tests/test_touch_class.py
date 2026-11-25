"""Touch styles and behavior key on a `touch` class on <html>, set before first
paint on a touch device, so that a page can also be shown as on a touch device
(the docs' Mouse / Touch switch sets the class). Leo approved this 2026-11-24."""

import re
from pathlib import Path

import rsm

ROOT = Path(__file__).resolve().parents[1]
BRAIID = (ROOT / "braiid" / "braiid.css").read_text()
HANDRAILS = (ROOT / "rsm" / "static" / "handrails.js").read_text()

TOUCH_QUERY = "(hover: none) and (pointer: coarse)"


def test_built_page_marks_touch_devices_before_first_paint():
    html = rsm.build(source="# T\n\nText.\n", standalone=False)
    head = html.split("</head>")[0]
    script = re.search(r"<script>[^<]*classList\.add\('touch'\)[^<]*</script>", head)
    assert script, "no pre-paint script that adds the touch class"
    assert TOUCH_QUERY in script.group(0)


def test_braiid_touch_rules_key_on_the_touch_class():
    assert TOUCH_QUERY not in BRAIID
    assert "html.touch" in BRAIID


def test_handrails_reads_touch_from_the_class():
    assert TOUCH_QUERY not in HANDRAILS
    assert "classList.contains(\"touch\")" in HANDRAILS
