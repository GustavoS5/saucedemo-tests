"""Checkout page object for the saucedemo site.

The saucedemo checkout spans two screens: step one collects the customer's
information (/checkout-step-one.html) and step two reviews the order summary
(/checkout-step-two.html). This page object groups both steps together.
"""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Represents the checkout flow (steps one and two)."""

    url = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.get_by_test_id("title")

        # Step one — customer information
        self.first_name_input = page.get_by_test_id("firstName")
        self.last_name_input = page.get_by_test_id("lastName")
        self.postal_code_input = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.error_message = page.get_by_test_id("error")

        # Step two — order summary
        self.finish_button = page.get_by_test_id("finish")
        self.complete_header = page.get_by_test_id("complete-header")
        self.summary_items = page.get_by_test_id("inventory-item")

    def fill_customer_info(
        self, first_name: str, last_name: str, postal_code: str
    ) -> None:
        """Fill out the checkout customer information form."""
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)

    def continue_to_overview(self) -> None:
        """Submit the customer info form to reach the order overview."""
        self.continue_button.click()

    def complete_order(self) -> None:
        """Finalize the order from the overview screen."""
        self.finish_button.click()
