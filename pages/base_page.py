"""Base page object for the Playwright Page Object Model."""

from __future__ import annotations


class BasePage:
    """Common state and navigation shared by every page object."""

    # Subclasses override this with the page's path (relative to base_url).
    url: str = ""

    def __init__(self, page) -> None:
        self.page = page

    def navigate(self):
        """Open the page via `page.goto()`, resolved against `--base-url`."""
        return self.page.goto(self.url)

    @property
    def current_url(self) -> str:
        """The page's current full URL."""
        return self.page.url
