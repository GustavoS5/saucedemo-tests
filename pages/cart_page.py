"""Shopping cart page object for the saucedemo site."""

from __future__ import annotations

from pages.base_page import BasePage


class CartPage(BasePage):
    """Represents /cart.html — the shopping cart review screen."""

    url = "/cart.html"

    def __init__(self, page) -> None:
        super().__init__(page)
        self.title = page.get_by_test_id("title")
        self.cart_items = page.get_by_test_id("inventory-item")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def get_item_names(self) -> list[str]:
        """Return the names of all items currently in the cart."""
        self.cart_items.get_by_test_id("inventory-item-name").wait_for()
        return [
            el.inner_text()
            for el in self.cart_items.get_by_test_id("inventory-item-name").all()
        ]

    def has_item(self, item_name: str) -> bool:
        """Return True if a specific item is present in the cart."""
        return item_name in self.get_item_names()

    def has_items(self, item_names: list[str]) -> bool:
        """Return True if every item in `item_names` is present in the cart."""
        present = set(self.get_item_names())
        return set(item_names).issubset(present)

    def remove_item(self, item_name: str):
        """Remove an item from the cart by its name."""
        self.cart_items.filter(has_text=item_name).get_by_role(
            "button", name="Remove"
        ).click()

    def go_to_checkout(self):
        """Proceed to the first checkout step."""
        self.checkout_button.click()
