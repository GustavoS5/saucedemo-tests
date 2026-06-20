"""Inventory (product list) page object for the saucedemo site."""

from __future__ import annotations

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Represents /inventory.html — the product catalogue after login."""

    url = "/inventory.html"

    def __init__(self, page) -> None:
        super().__init__(page)
        self.title = page.get_by_test_id("title")
        self.inventory_items = page.get_by_test_id("inventory-item")
        self.shopping_cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.shopping_cart_link = page.get_by_test_id("shopping-cart-link")
        self.sort_dropdown = page.get_by_test_id("product-sort-container")

    # --- Cart interactions ---
    def add_item_to_cart(self, item_name: str):
        """Click the 'Add to cart' button for a product by its name."""
        self.page.get_by_test_id("inventory-item").filter(
            has_text=item_name
        ).get_by_role("button", name="Add to cart").click()

    def remove_item_from_cart(self, item_name: str):
        """Click the 'Remove' button for a product by its name."""
        self.page.get_by_test_id("inventory-item").filter(
            has_text=item_name
        ).get_by_role("button", name="Remove").click()

    def go_to_cart(self):
        """Open the shopping cart."""
        self.shopping_cart_link.click()
