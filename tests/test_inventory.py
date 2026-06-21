"""Inventory (product list) tests for the saucedemo site."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect


@pytest.mark.parametrize("item_name", ["Sauce Labs Backpack", "Sauce Labs Bike Light"])
def test_add_item_to_cart(inventory_page, item_name):
    inventory_page.add_item_to_cart(item_name)
    expect(inventory_page.shopping_cart_badge).to_have_text("1")


def test_add_multiple_items_to_cart(inventory_page):
    inventory_page.add_item_to_cart("Sauce Labs Backpack")
    inventory_page.add_item_to_cart("Sauce Labs Bike Light")
    expect(inventory_page.shopping_cart_badge).to_have_text("2")


def test_remove_item_from_cart(inventory_page):
    inventory_page.add_item_to_cart("Sauce Labs Backpack")
    inventory_page.remove_item_from_cart("Sauce Labs Backpack")
    expect(inventory_page.shopping_cart_badge).to_be_hidden()
