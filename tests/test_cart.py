"""Shopping cart tests for the saucedemo site."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_cart_contains_expected_item(cart_page_with_item):
    expect(cart_page_with_item.get_item_locator("Sauce Labs Backpack")).to_be_visible()


def test_cart_after_remove_is_empty(cart_page_with_item):
    cart_page_with_item.remove_item("Sauce Labs Backpack")
    expect(cart_page_with_item.get_item_names_locator()).to_have_count(0)


def test_cart_shows_multiple_items(cart_page_with_multiple_items):
    expect(cart_page_with_multiple_items.get_item_names_locator()).to_have_count(3)


def test_remove_one_item_from_cart(cart_page_with_multiple_items):
    cart_page_with_multiple_items.remove_item("Sauce Labs Bolt T-Shirt")
    expect(cart_page_with_multiple_items.get_item_names_locator()).to_have_count(2)
    expect(
        cart_page_with_multiple_items.get_item_locator("Sauce Labs Bolt T-Shirt")
    ).not_to_be_visible()


def test_cart_is_empty_after_removing_all_items(cart_page_with_multiple_items):
    cart_page_with_multiple_items.remove_item("Sauce Labs Backpack")
    cart_page_with_multiple_items.remove_item("Sauce Labs Bolt T-Shirt")
    cart_page_with_multiple_items.remove_item("Sauce Labs Onesie")
    expect(cart_page_with_multiple_items.get_item_names_locator()).to_have_count(0)


def test_cart_persists_items_after_navigation(cart_page_with_item):
    """Items remain in the cart after navigating away and back."""
    expect(cart_page_with_item.get_item_locator("Sauce Labs Backpack")).to_be_visible()

    cart_page_with_item.continue_shopping_button.click()

    inventory = InventoryPage(cart_page_with_item.page)
    inventory.go_to_cart()

    expect(cart_page_with_item.get_item_locator("Sauce Labs Backpack")).to_be_visible()
    expect(cart_page_with_item.get_item_names_locator()).to_have_count(1)


def test_cart_prices_match_inventory(cart_page_with_multiple_items):
    """Cart item prices should match the prices shown on the inventory page."""
    cart = cart_page_with_multiple_items
    inventory = InventoryPage(cart.page)

    items = ["Sauce Labs Backpack", "Sauce Labs Bolt T-Shirt", "Sauce Labs Onesie"]

    inventory.navigate()
    inventory_prices = {item: inventory.get_item_price(item) for item in items}

    cart.navigate()
    for item in items:
        expect(cart.get_item_price_locator(item)).to_have_text(inventory_prices[item])
