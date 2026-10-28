"""The fold label at the foot of a folded block's handrail (rsm-85x).

A folded block says what it hides: "N steps hidden", "justification hidden" for
a step whose only hidden body is its :p:, else "<kind> hidden". The words come
from data-fold-label and CSS draws them. A proof draws its label from its
.hr-label, so the tombstone (the proof content zone's ::after) is untouched.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

FOLDED = ".proof.hr[data-start-collapsed]"
PROOF_HEAD = FOLDED + " > .hr-content-zone > .hr-label"
PROOF_ZONE = FOLDED + " > .hr-content-zone"
OPEN = "#prf-open"

STYLE_KEYS = ["content", "display", "fontStyle", "fontSize", "color", "left", "top", "position"]
TOMBSTONE_KEYS = ["content", "position", "width", "height", "backgroundColor", "borderRadius"]


def _load(page: Page, server: str, width: int = 1280, theme: str = "light") -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.emulate_media(color_scheme=theme)
    page.goto(f"{server}/fold-label.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _pseudo(page: Page, selector: str, keys=STYLE_KEYS, which: str = "::after") -> dict:
    return page.evaluate(
        """([sel, keys, which]) => {
            const cs = getComputedStyle(document.querySelector(sel), which);
            return Object.fromEntries(keys.map(k => [k, cs[k]]));
        }""",
        [selector, keys, which],
    )


def _label_text(page: Page, selector: str) -> str | None:
    """The text a fold label pseudo-element shows, or None when it shows none."""
    return page.evaluate(
        """sel => {
            const el = document.querySelector(sel);
            const content = getComputedStyle(el, "::after").content;
            if (content === "none" || content === "normal") return null;
            if (content === "attr(data-fold-label)") return el.getAttribute("data-fold-label");
            return content.replace(/^"|"$/g, "");
        }""",
        selector,
    )


def _dark(page: Page) -> str:
    # The resolved colour of --dark in the current theme.
    return page.evaluate(
        """() => {
            const probe = document.createElement("span");
            probe.style.color = "var(--dark)";
            document.querySelector(".manuscriptwrapper").appendChild(probe);
            const c = getComputedStyle(probe).color;
            probe.remove();
            return c;
        }"""
    )


def _fold_step(page: Page, step_id: str) -> None:
    step = page.locator(f"#{step_id}")
    step.locator(":scope > .hr-border-zone .hr-border-dots").click()
    page.locator("#hr-menu-singleton [data-role='collapse']").click()
    expect(step).to_have_class(re.compile(r"\bhr-collapsed\b"))


def _unfold_proof(page: Page) -> None:
    page.locator(FOLDED + " > .hr-collapse-zone .hr-collapse").click()
    expect(page.locator(FOLDED)).not_to_have_class(re.compile(r"\bhr-collapsed\b"))


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_folded_proof_label_on_load(page: Page, interactive_server: str, width, theme):
    _load(page, interactive_server, width, theme)
    expect(page.locator(FOLDED)).to_have_class(re.compile(r"\bhr-collapsed\b"))
    assert _label_text(page, PROOF_HEAD) == "3 steps hidden"
    style = _pseudo(page, PROOF_HEAD)
    assert style["fontStyle"] == "italic"
    root = page.evaluate("() => parseFloat(getComputedStyle(document.documentElement).fontSize)")
    assert float(style["fontSize"].removesuffix("px")) == pytest.approx(0.875 * root)
    assert style["color"] == _dark(page)
    assert style["position"] == "relative"
    # No step count in the header any more.
    expect(page.locator(".proof-step-count")).to_have_count(0)


def test_proof_label_matches_step_label_style(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _unfold_proof(page)
    _fold_step(page, "stp-sub")
    page.locator(FOLDED + " > .hr-collapse-zone .hr-collapse").click()
    expect(page.locator(FOLDED)).to_have_class(re.compile(r"\bhr-collapsed\b"))
    proof = _pseudo(page, PROOF_HEAD)
    step = _pseudo(page, "#stp-sub > .hr-content-zone")
    for key in ("fontStyle", "fontSize", "color", "left", "position"):
        assert proof[key] == step[key], key


def test_open_proof_shows_no_label(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _unfold_proof(page)
    assert _label_text(page, PROOF_HEAD) is None


@pytest.mark.parametrize("how", ["hover", "focus"])
def test_hover_and_focus_keep_label_and_tombstone(page: Page, interactive_server: str, how):
    _load(page, interactive_server)
    before = _pseudo(page, PROOF_HEAD)

    # The tombstone of an open proof under the same interaction is the reference.
    open_proof = page.locator(OPEN)
    getattr(open_proof, how)()
    reference = _pseudo(page, f"{OPEN} > .hr-content-zone", TOMBSTONE_KEYS)
    assert reference["content"] == '""'

    folded = page.locator(FOLDED)
    page.mouse.move(0, 0)
    getattr(folded, how)()
    assert _pseudo(page, PROOF_HEAD) == before
    assert _label_text(page, PROOF_HEAD) == "3 steps hidden"
    assert _pseudo(page, PROOF_ZONE, TOMBSTONE_KEYS) == reference


def test_step_with_substeps_label(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _unfold_proof(page)
    _fold_step(page, "stp-sub")
    assert _label_text(page, "#stp-sub > .hr-content-zone") == "2 steps hidden"


def test_step_with_only_justification_label(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _unfold_proof(page)
    _fold_step(page, "stp-just")
    assert _label_text(page, "#stp-just > .hr-content-zone") == "justification hidden"


def test_calc_step_has_no_label(page: Page, interactive_server: str):
    # Calc rows start folded, so a label under every relation would be noise.
    _load(page, interactive_server)
    row = page.locator(".calc > .step").first
    expect(row).to_have_class(re.compile(r"\bhr-collapsed\b"))
    zone = ".calc > .step > .hr-content-zone"
    assert page.locator(zone).first.get_attribute("data-fold-label") is None
    assert _label_text(page, zone) is None


@pytest.mark.parametrize("block,word", [(".sketch.hr", "sketch hidden"), (".lemma.hr", "lemma hidden")])
def test_labelled_blocks_without_steps(page: Page, interactive_server: str, block, word):
    _load(page, interactive_server)
    page.locator(f"{block} > .hr-collapse-zone .hr-collapse").click()
    expect(page.locator(block)).to_have_class(re.compile(r"\bhr-collapsed\b"))
    assert _label_text(page, f"{block} > .hr-content-zone > .hr-label") == word


def test_collapse_button_names_what_is_hidden(page: Page, interactive_server: str):
    _load(page, interactive_server)
    btn = page.locator(FOLDED + " > .hr-collapse-zone .hr-collapse")
    expect(btn).to_have_attribute("aria-label", re.compile(r"^Show .+, 3 steps hidden$"))
    btn.click()
    expect(btn).to_have_attribute("aria-label", re.compile(r"^Hide "))
    assert "hidden" not in btn.get_attribute("aria-label")


def test_print_drops_labels(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _unfold_proof(page)
    _fold_step(page, "stp-just")
    page.locator(FOLDED + " > .hr-collapse-zone .hr-collapse").click()
    assert _label_text(page, PROOF_HEAD) == "3 steps hidden"
    assert _label_text(page, "#stp-just > .hr-content-zone") == "justification hidden"
    page.emulate_media(media="print")
    assert _label_text(page, PROOF_HEAD) is None
    assert _label_text(page, "#stp-just > .hr-content-zone") is None
