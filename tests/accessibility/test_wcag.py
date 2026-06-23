"""WCAG 2.1 AA compliance tests using axe-core."""

from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page


@pytest.mark.accessibility
class TestWCAGCompliance:
    """Automated accessibility tests for WCAG 2.1 AA compliance."""

    def test_light_theme_wcag_aa(
        self,
        serve_rsm_a11y: callable,
        page: Page,
    ) -> None:
        """
        Verify light theme meets WCAG 2.1 AA standards.

        Tests: color contrast, ARIA labels, semantic HTML, keyboard access.
        """
        fixture = Path(__file__).parent.parent / "visual" / "fixtures" / "block-types.rsm"
        page = serve_rsm_a11y(fixture.read_text(), dark_theme=False)

        axe = Axe()
        results = axe.run(page)

        assert len(results.response["violations"]) == 0, self._format_violations(results.response["violations"])

    def test_dark_theme_wcag_aa(
        self,
        serve_rsm_a11y: callable,
        page: Page,
    ) -> None:
        """
        Verify dark theme meets WCAG 2.1 AA standards.

        Tests: color contrast in dark mode, proper theme switching.
        """
        fixture = Path(__file__).parent.parent / "visual" / "fixtures" / "block-types.rsm"
        page = serve_rsm_a11y(fixture.read_text(), dark_theme=True)

        axe = Axe()
        results = axe.run(page)

        assert len(results.response["violations"]) == 0, self._format_violations(results.response["violations"])

    def test_interactive_elements_accessible(
        self,
        serve_rsm_a11y: callable,
        page: Page,
    ) -> None:
        """
        Verify interactive elements (handrails, buttons) are accessible.

        Tests: ARIA labels, keyboard navigation, focus indicators.
        """
        fixture = Path(__file__).parent.parent / "visual" / "fixtures" / "interactive-states.rsm"
        page = serve_rsm_a11y(fixture.read_text())

        axe = Axe()
        # Focus on interactive element rules
        results = axe.run(page, options={
            "runOnly": {
                "type": "tag",
                "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"]
            }
        })

        assert len(results.response["violations"]) == 0, self._format_violations(results.response["violations"])

    def test_document_structure_semantic(
        self,
        serve_rsm_a11y: callable,
        page: Page,
    ) -> None:
        """
        Verify document structure uses semantic HTML properly.

        Tests: heading hierarchy, landmark regions, list structure.
        """
        fixture = Path(__file__).parent.parent / "visual" / "fixtures" / "block-types.rsm"
        page = serve_rsm_a11y(fixture.read_text())

        axe = Axe()
        # Focus on document structure rules
        results = axe.run(page, options={
            "rules": {
                "heading-order": {"enabled": True},
                "landmark-one-main": {"enabled": True},
                "page-has-heading-one": {"enabled": True},
                "region": {"enabled": True},
            }
        })

        assert len(results.response["violations"]) == 0, self._format_violations(results.response["violations"])

    @pytest.mark.parametrize("dark_theme", [False, True])
    def test_front_matter_landmarks_and_headings(
        self,
        serve_rsm_a11y: callable,
        page: Page,
        dark_theme: bool,
    ) -> None:
        """Front matter (abstract + table of contents) accessibility.

        The shared visual fixtures have no abstract or :toc:, so this exercises
        the front-matter specific guarantees: the abstract/TOC headings are
        emitted at semantic level 2 (no h1->h3 skip, WCAG 1.3.1 heading-order),
        the TOC is a named navigation landmark, and each TOC link exposes its
        full section title as an accessible name (not just the secnum). Run in
        both themes so the front-matter eyebrow's contrast holds in dark mode.
        """
        src = (
            "# Front matter accessibility\n\n"
            ":abstract:\n"
            "  An abstract paragraph for the accessibility fixture.\n"
            "::\n\n"
            ":toc:\n\n"
            "## Introduction\n\nIntro body.\n\n"
            "## Methods\n\nMethods body.\n\n"
            "### Details\n\nDetails body.\n"
        )
        page = serve_rsm_a11y(src, dark_theme)

        axe = Axe()
        results = axe.run(page, options={
            "runOnly": {
                "type": "tag",
                "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"],
            }
        })
        assert len(results.response["violations"]) == 0, self._format_violations(results.response["violations"])

        # TOC is a navigation landmark with an accessible name.
        assert page.locator('nav.toc[aria-label="Table of contents"]').count() == 1

        # Abstract heading is level 2, not the old level 3 (no h1->h3 skip).
        assert page.locator(".abstract h2").count() == 1
        assert page.locator(".abstract h3").count() == 0

        # TOC links carry their full "num. title" as the accessible name.
        labels = page.eval_on_selector_all(
            "nav.toc a", "els => els.map(e => e.getAttribute('aria-label'))"
        )
        assert any(lbl and "Introduction" in lbl for lbl in labels), labels

    def test_keyboard_navigation(
        self,
        serve_rsm_a11y: callable,
        page: Page,
    ) -> None:
        """
        Verify all interactive elements are keyboard accessible.

        Tests: focusable elements, tab order, focus visibility.
        """
        fixture = Path(__file__).parent.parent / "visual" / "fixtures" / "interactive-states.rsm"
        page = serve_rsm_a11y(fixture.read_text())

        # Get all focusable elements
        focusable_selector = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        focusable_count = page.locator(focusable_selector).count()

        # Should have focusable elements
        assert focusable_count > 0, "No focusable elements found on page"

        # Tab through all focusable elements
        for _ in range(focusable_count):
            page.keyboard.press("Tab")

            # Verify something is focused
            focused_element = page.evaluate("() => document.activeElement?.tagName")
            assert focused_element is not None, "Tab did not focus any element"

        # Run axe for keyboard-specific issues
        axe = Axe()
        results = axe.run(page, options={
            "runOnly": {
                "type": "tag",
                "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "keyboard"]
            }
        })

        assert len(results.response["violations"]) == 0, self._format_violations(results.response["violations"])

    def test_all_accent_color_contrast(
        self,
        page: Page,
    ) -> None:
        """
        Verify all accent colors meet WCAG 2.1 AA color contrast (4.5:1).

        Tests all 32 combinations: 8 colors × 2 themes × 2 shades (default + hover).
        Uses 16 HTML files (one per color/theme combination) served via HTTP.
        """
        import http.server
        import socketserver
        import threading
        import os

        colors = ["blue", "purple", "red", "green", "orange", "yellow", "pink", "gray"]
        themes = ["light", "dark"]

        # Start HTTP server from project root
        original_dir = os.getcwd()
        os.chdir(Path(__file__).parent.parent.parent)  # Navigate to rsm root

        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("127.0.0.1", 0), handler) as s:
            port = s.server_address[1]

        class ThreadedHTTPServer(socketserver.TCPServer):
            allow_reuse_address = True

        server = ThreadedHTTPServer(("127.0.0.1", port), handler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        try:
            all_violations = []

            # Test each color/theme combination
            for color in colors:
                for theme in themes:
                    filename = f"accent-{color}-{theme}.html"
                    page.goto(f"http://127.0.0.1:{port}/tests/accessibility/fixtures/{filename}")
                    page.wait_for_load_state("domcontentloaded")

                    # Debug: check actual rendered colors
                    default_color = page.locator('a:first-of-type').evaluate("el => getComputedStyle(el).color")
                    hover_color = page.locator('a:nth-of-type(2)').evaluate("el => getComputedStyle(el).color")
                    bg_color = page.locator('body').evaluate("el => getComputedStyle(el).backgroundColor")
                    print(f"{color} {theme}: default={default_color}, hover={hover_color}, bg={bg_color}")

                    axe = Axe()
                    results = axe.run(page, options={
                        "runOnly": {
                            "type": "rule",
                            "values": ["color-contrast"]
                        }
                    })
                    if results.response["violations"]:
                        all_violations.extend([(f"{color.title()} {theme.title()}", v) for v in results.response["violations"]])

            # Format combined violations
            if all_violations:
                formatted = [f"\nFound {len(all_violations)} accessibility violations:\n"]
                for label, violation in all_violations:
                    formatted.append(f"\n[{label}] {violation['id']}: {violation['description']}")
                    formatted.append(f"  Impact: {violation['impact']}")
                    for node in violation.get('nodes', [])[:3]:
                        formatted.append(f"  - {node.get('html', 'Unknown element')}")
                        if 'failureSummary' in node:
                            formatted.append(f"    {node['failureSummary']}")
                assert False, "\n".join(formatted)

            assert len(all_violations) == 0
        finally:
            server.shutdown()
            os.chdir(original_dir)

    def _format_violations(self, violations: list) -> str:
        """Format axe violations into readable error message."""
        if not violations:
            return ""

        lines = [f"\nFound {len(violations)} accessibility violations:\n"]

        for v in violations:
            lines.append(f"\n{v['id']}: {v['description']}")
            lines.append(f"  Impact: {v['impact']}")
            lines.append(f"  Help: {v['help']}")
            lines.append(f"  WCAG: {', '.join(v.get('tags', []))}")

            # Show first few affected elements
            nodes = v.get('nodes', [])[:3]
            for node in nodes:
                lines.append(f"  - {node.get('html', 'Unknown element')}")
                if 'failureSummary' in node:
                    lines.append(f"    {node['failureSummary']}")

        return "\n".join(lines)
