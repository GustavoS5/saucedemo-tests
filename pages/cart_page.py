"""Shopping cart page object for the saucedemo site."""

from __future__ import annotations

from pages.base_page import BasePage


class CartPage(BasePage):
    """Represents /cart.html — the shopping cart review screen."""

    url = "/cart.html"

    def __init__(self, page) -> None:
        super().__init__(page)
        self.title = page.get_by_test_id("title")
        self.cart_items = page.get_by_test_id("cart-item")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def remove_item(self, item_name: str):
        """Remove an item from the cart by its name."""
        self.cart_items.filter(has_text=item_name).get_by_role(
            "button", name="Remove"
        ).click()

    def go_to_checkout(self):
        """Proceed to the first checkout step."""
        self.checkout_button.click()
