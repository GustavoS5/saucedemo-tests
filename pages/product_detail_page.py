"""Product detail page object for the saucedemo site."""

from __future__ import annotations

from playwright.sync_api import Page, Response

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    """Represents /inventory-item.html — reached via an item link, not direct navigation."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.back_to_products_button = page.get_by_test_id("back-to-products")
        self.item_name = page.get_by_test_id("inventory-item-name")
        self.item_desc = page.get_by_test_id("inventory-item-desc")
        self.item_price = page.get_by_test_id("inventory-item-price")
        self.add_to_cart_button = page.get_by_role("button", name="Add to cart")
        self.remove_button = page.get_by_role("button", name="Remove")

    def navigate(self) -> Response | None:
        raise NotImplementedError(
            "ProductDetailPage has no stable direct URL; open it via "
            "InventoryPage.open_item() instead."
        )

    def go_back_to_products(self) -> None:
        """Click 'Back to products' to return to the inventory list."""
        self.back_to_products_button.click()

    def get_name(self) -> str:
        """Return the product name shown on the detail page."""
        return self.item_name.inner_text()

    def get_description(self) -> str:
        """Return the product description shown on the detail page."""
        return self.item_desc.inner_text()

    def get_price(self) -> str:
        """Return the product price shown on the detail page."""
        return self.item_price.inner_text()

    def add_to_cart(self) -> None:
        """Click 'Add to cart' from the detail page."""
        self.add_to_cart_button.click()
