"""Reusable footer component for the saucedemo site.

The footer appears on several pages (inventory, cart, etc.), so it is modelled
as a component rather than a full page object.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page


class FooterComponent:
    """Social links and copyright footer shared across pages."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.footer = page.get_by_test_id("footer")
        self.copyright = page.get_by_test_id("footer-copy")
        self.twitter_link = page.get_by_test_id("social-twitter")
        self.facebook_link = page.get_by_test_id("social-facebook")
        self.linkedin_link = page.get_by_test_id("social-linkedin")
        self.social_links = page.locator('[data-test="footer"] a')

    def get_social_link(self, data_test: str) -> Locator:
        """Return a social link by its data-test id."""
        return self.page.get_by_test_id(data_test)
