"""Footer tests for the saucedemo site.

The footer is a shared component, so these tests run from a logged-in
inventory page but focus only on footer rendering and links.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.footer_component import FooterComponent


@pytest.fixture
def footer(inventory_page) -> FooterComponent:
    """Footer component bound to an authenticated inventory page."""
    return FooterComponent(inventory_page.page)


def test_footer_is_visible(footer: FooterComponent):
    """The footer is rendered on the inventory page."""
    expect(footer.footer).to_be_visible()


def test_footer_copyright_text(footer: FooterComponent):
    """The footer shows the Sauce Labs copyright notice."""
    expect(footer.copyright).to_contain_text("Sauce Labs")
    expect(footer.copyright).to_contain_text("All Rights Reserved")


@pytest.mark.parametrize(
    "data_test, expected_href",
    [
        pytest.param(
            "social-twitter",
            "https://twitter.com/saucelabs",
            id="twitter",
        ),
        pytest.param(
            "social-facebook",
            "https://www.facebook.com/saucelabs",
            id="facebook",
        ),
        pytest.param(
            "social-linkedin",
            "https://www.linkedin.com/company/sauce-labs/",
            id="linkedin",
        ),
    ],
)
def test_social_links_have_correct_href(
    footer: FooterComponent, data_test: str, expected_href: str
):
    """Each social link is visible and points to the expected Sauce Labs URL."""
    link = footer.get_social_link(data_test)
    expect(link).to_be_visible()
    expect(link).to_have_attribute("href", expected_href)


def test_footer_links_are_anchors(footer: FooterComponent):
    """The three social links are anchor elements (clickable links)."""
    expect(footer.social_links).to_have_count(3)
