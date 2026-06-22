"""Shopping cart page object for the saucedemo site."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class CartPage(BasePage):
    """Represents /cart.html — the shopping cart review screen."""

    url = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.title = page.get_by_test_id("title")
        self.cart_items = page.get_by_test_id("inventory-item")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def get_item_names_locator(self) -> Locator:
        return self.cart_items.get_by_test_id("inventory-item-name")

    def get_item_names(self) -> list[str]:
        """Return the names of all items currently in the cart."""
        self.get_item_names_locator().wait_for()
        return [el.inner_text() for el in self.get_item_names_locator().all()]

    def get_item_locator(self, item_name: str) -> Locator:
        return self.cart_items.filter(has_text=item_name)

    def has_item(self, item_name: str) -> bool:
        """Return True if a specific item is present in the cart."""
        return item_name in self.get_item_names()

    def has_items(self, item_names: list[str]) -> bool:
        """Return True if every item in `item_names` is present in the cart."""
        present = set(self.get_item_names())
        return set(item_names).issubset(present)

    def remove_item(self, item_name: str) -> None:
        """Remove an item from the cart by its name."""
        self.cart_items.filter(has_text=item_name).get_by_role(
            "button", name="Remove"
        ).click()

    def get_item_price_locator(self, item_name: str) -> Locator:
        """Return the price locator for a specific cart item."""
        return self.cart_items.filter(
            has=self.page.get_by_test_id("inventory-item-name").filter(
                has_text=item_name
            )
        ).get_by_test_id("inventory-item-price")

    def get_item_price(self, item_name: str) -> str:
        price = self.get_item_price_locator(item_name)
        price.wait_for()
        return str(price.inner_text())

    def go_to_checkout(self) -> None:
        """Proceed to the first checkout step."""
        self.checkout_button.click()
