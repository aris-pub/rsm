"""Tests for toast notification behavior in direct and iframe contexts.

The iframe tests navigate with wait_until="domcontentloaded", not the default
"load": a pending iframe sub-resource can keep the parent page's load event from
firing, which made page.goto time out at 30s (potf-d2l). Each test waits for the
frame's own content explicitly afterward, so it never needed the load event.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def wait_for_rsm(page):
    page.wait_for_function(RSM_READY, timeout=10_000)


def wait_for_rsm_in_frame(page, selector="#rsm-frame"):
    # Wait for the iframe's OWN init signal, not just its DOM. After
    # domcontentloaded the frame's scripts may not have wired the handrails yet,
    # so a click would hit a menu that has not been built (potf-d2l). Returns the
    # frame_locator for the caller to interact with.
    handle = page.wait_for_selector(selector, state="attached")
    handle.content_frame().wait_for_function(RSM_READY, timeout=10_000)
    return page.frame_locator(selector)


def trigger_copy_link(page_or_frame, *, selector=".hr:not(.hr-hidden)"):
    """Click the handrail dots to open the menu, then click the copy-link item.

    The open menu is portaled to <body> out of the handrail (handrails.js), so the
    copy-link item is reached via the singleton, not under the handrail."""
    page_or_frame.locator(f"{selector} .hr-border-dots").first.click()
    page_or_frame.locator(
        "#hr-menu-singleton .hr-menu-item.link:not(.disabled)"
    ).first.click()


class TestToastsDirect:
    """Toast behavior when RSM document is loaded directly (not in an iframe)."""

    def test_success_toast_appears_on_copy_link(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/basic.html")
        wait_for_rsm(page)
        trigger_copy_link(page)
        expect(page.locator(".toast.success")).to_be_visible()

    def test_success_toast_disappears_after_timeout(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/basic.html")
        wait_for_rsm(page)
        trigger_copy_link(page)
        expect(page.locator(".toast.success")).to_be_visible()
        # Toast auto-removes after 5s; allow up to 7s for timing slack
        expect(page.locator(".toast.success")).to_be_hidden(timeout=7_000)

    def test_toast_can_be_dismissed_manually(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/basic.html")
        wait_for_rsm(page)
        trigger_copy_link(page)
        toast = page.locator(".toast.success")
        expect(toast).to_be_visible()
        toast.locator(".icon.close").click()
        expect(toast).to_be_hidden()


class TestToastsUnsandboxedIframe:
    """Toast behavior when RSM document runs inside an unsandboxed iframe (mirrors Press)."""

    def test_success_toast_appears_in_unsandboxed_iframe(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/iframe-unsandboxed.html", wait_until="domcontentloaded")
        frame = wait_for_rsm_in_frame(page)
        frame.locator(".hr:not(.hr-hidden) .hr-border-dots").first.click()
        frame.locator("#hr-menu-singleton .hr-menu-item.link:not(.disabled)").first.click()
        expect(frame.locator(".toast.success")).to_be_visible()

    def test_toast_renders_inside_iframe_not_in_parent(self, page: Page, interactive_server: str):
        """Toast must appear inside the iframe document, not escape to the parent."""
        page.goto(f"{interactive_server}/iframe-unsandboxed.html", wait_until="domcontentloaded")
        frame = wait_for_rsm_in_frame(page)
        frame.locator(".hr:not(.hr-hidden) .hr-border-dots").first.click()
        frame.locator("#hr-menu-singleton .hr-menu-item.link:not(.disabled)").first.click()
        expect(frame.locator(".toast")).to_be_visible()
        expect(page.locator(".toast")).to_have_count(0)


class TestToastsSandboxedIframe:
    """Toast behavior when RSM document runs inside a sandboxed iframe (mirrors Sphinx docs).

    sandbox="allow-scripts allow-same-origin" blocks the clipboard API, so copy-link
    triggers the error toast instead of the success toast.
    """

    def test_error_toast_appears_when_clipboard_blocked(self, page: Page, interactive_server: str):
        """When clipboard is blocked in a sandboxed iframe, the error toast must appear.

        NOTE: Chromium grants clipboard access to sandboxed iframes when the browser
        context has clipboard-write permission (as set in browser_context_args), so this
        test uses a context WITHOUT that permission to simulate a real user's browser.
        """
        context = page.context.browser.new_context()
        isolated_page = context.new_page()
        try:
            isolated_page.goto(f"{interactive_server}/iframe-sandboxed.html", wait_until="domcontentloaded")
            frame = wait_for_rsm_in_frame(isolated_page)
            frame.locator(".hr:not(.hr-hidden) .hr-border-dots").first.click()
            frame.locator("#hr-menu-singleton .hr-menu-item.link:not(.disabled)").first.click()
            expect(frame.locator(".toast.error")).to_be_visible()
        finally:
            context.close()

    def test_no_silent_crash_in_sandboxed_iframe(self, page: Page, interactive_server: str):
        """Some toast (success or error) must always appear — never a silent crash."""
        page.goto(f"{interactive_server}/iframe-sandboxed.html", wait_until="domcontentloaded")
        frame = wait_for_rsm_in_frame(page)
        frame.locator(".hr:not(.hr-hidden) .hr-border-dots").first.click()
        frame.locator("#hr-menu-singleton .hr-menu-item.link:not(.disabled)").first.click()
        expect(frame.locator(".toast")).to_be_visible()
