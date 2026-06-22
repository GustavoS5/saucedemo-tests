"""Inventory (product list) page object for the saucedemo site."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Represents /inventory.html — the product catalogue after login."""

    url = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.get_by_test_id("title")
        self.inventory_items = page.get_by_test_id("inventory-item")
        self.shopping_cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.shopping_cart_link = page.get_by_test_id("shopping-cart-link")
        self.sort_dropdown = page.get_by_test_id("product-sort-container")
        self.menu_button = page.get_by_role("button", name="Open Menu")
        self.logout_link = page.get_by_role("link", name="Logout")

    def _item_locator(self, item_name: str) -> Locator:
        """Return the inventory-item block matching `item_name` by its title."""
        return self.inventory_items.filter(
            has=self.page.get_by_test_id("inventory-item-name").filter(
                has_text=item_name
            )
        )

    def add_item_to_cart(self, item_name: str) -> None:
        """Click the 'Add to cart' button for a product by its name."""
        self._item_locator(item_name).get_by_role("button", name="Add to cart").click()

    def remove_item_from_cart(self, item_name: str) -> None:
        """Click the 'Remove' button for a product by its name."""
        self._item_locator(item_name).get_by_role("button", name="Remove").click()

    def go_to_cart(self) -> None:
        """Open the shopping cart."""
        self.shopping_cart_link.click()

    def get_item_price(self, item_name: str) -> str:
        price = self._item_locator(item_name).get_by_test_id("inventory-item-price")
        price.wait_for()
        return price.inner_text()

    def sort_by(self, option: str) -> None:
        """Select a sort option ('az', 'za', 'lohi', 'hilo')."""
        self.sort_dropdown.select_option(option)

    def get_item_names_in_order(self) -> list[str]:
        """Return the inventory item names in their current display order."""
        names = self.page.get_by_test_id("inventory-item-name")
        names.first.wait_for()
        return [el.inner_text() for el in names.all()]

    def get_item_prices_in_order(self) -> list[float]:
        """Return inventory item prices as floats in their display order."""
        prices = self.page.get_by_test_id("inventory-item-price")
        prices.first.wait_for()
        return [float(el.inner_text().replace("$", "")) for el in prices.all()]

    def open_item(self, item_name: str) -> None:
        """Click a product's name link to open its detail page."""
        self._item_locator(item_name).get_by_test_id("inventory-item-name").click()

    def logout(self) -> None:
        """Open the sidebar menu and click Logout."""
        self.menu_button.click()
        self.logout_link.click()
