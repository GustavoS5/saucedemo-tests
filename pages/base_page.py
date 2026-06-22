"""Base page object for the Playwright Page Object Model."""

from __future__ import annotations

from playwright.sync_api import Page, Response


class BasePage:
    """Common state and navigation shared by every page object."""

    url: str = ""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self) -> Response | None:
        """Open the page via `page.goto()`, resolved against `--base-url`."""
        return self.page.goto(self.url)

    @property
    def current_url(self) -> str:
        """The page's current full URL."""
        return str(self.page.url)
