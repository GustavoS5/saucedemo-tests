"""Inventory (product list) tests for the saucedemo site."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect
from pages.inventory_page import InventoryPage
from tests.conftest import inventory_page


@pytest.mark.parametrize("item_name", ["Sauce Labs Backpack", "Sauce Labs Bike Light"])
def test_add_item_to_cart(inventory_page, item_name):
    """Test that an item can be added to the cart."""
    inventory_page.add_item_to_cart(item_name)
    expect(inventory_page.shopping_cart_badge).to_have_text("1")