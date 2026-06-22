"""Cart persistence tests — verifying cart state across session cycles."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.mark.e2e
def test_cart_persists_after_logout_and_relogin(
    logged_in_page, saucedemo_credentials, base_url: str
):
    """Items added to the cart remain after a logout and log back in."""
    inventory = InventoryPage(logged_in_page)
    inventory.add_item_to_cart("Sauce Labs Backpack")
    expect(inventory.shopping_cart_badge).to_have_text("1")

    inventory.logout()
    expect(logged_in_page).to_have_url(f"{base_url}/")

    login = LoginPage(logged_in_page)
    login.login(
        saucedemo_credentials["username"],
        saucedemo_credentials["password"],
    )
    expect(logged_in_page).to_have_url(f"{base_url}/inventory.html")

    inventory_after = InventoryPage(logged_in_page)
    expect(inventory_after.shopping_cart_badge).to_have_text("1")

    inventory_after.go_to_cart()
    cart = CartPage(logged_in_page)
    expect(cart.get_item_locator("Sauce Labs Backpack")).to_be_visible()
    expect(cart.get_item_names_locator()).to_have_count(1)


@pytest.mark.e2e
def test_cart_persists_multiple_items_after_relogin(
    logged_in_page, saucedemo_credentials, base_url: str
):
    """Multiple cart items survive a logout/re-login cycle."""
    inventory = InventoryPage(logged_in_page)
    inventory.add_item_to_cart("Sauce Labs Backpack")
    inventory.add_item_to_cart("Sauce Labs Bike Light")
    inventory.add_item_to_cart("Sauce Labs Onesie")
    expect(inventory.shopping_cart_badge).to_have_text("3")

    inventory.logout()
    expect(logged_in_page).to_have_url(f"{base_url}/")

    login = LoginPage(logged_in_page)
    login.login(
        saucedemo_credentials["username"],
        saucedemo_credentials["password"],
    )

    inventory_after = InventoryPage(logged_in_page)
    expect(inventory_after.shopping_cart_badge).to_have_text("3")

    inventory_after.go_to_cart()
    cart = CartPage(logged_in_page)
    expect(cart.get_item_names_locator()).to_have_count(3)
    for expected in (
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Onesie",
    ):
        expect(cart.cart_items.filter(has_text=expected)).to_be_visible()


def test_cart_badge_updates_after_navigation_cycle(
    logged_in_page, saucedemo_credentials, base_url: str
):
    """The cart badge reflects the persisted count after re-login."""
    inventory = InventoryPage(logged_in_page)
    inventory.add_item_to_cart("Sauce Labs Backpack")
    inventory.add_item_to_cart("Sauce Labs Bolt T-Shirt")

    inventory.logout()

    login = LoginPage(logged_in_page)
    login.login(
        saucedemo_credentials["username"],
        saucedemo_credentials["password"],
    )

    inventory_after = InventoryPage(logged_in_page)
    expect(inventory_after.shopping_cart_badge).to_have_text("2")
