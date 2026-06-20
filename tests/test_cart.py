"""Shopping cart tests for the saucedemo site."""

from __future__ import annotations
from playwright.sync_api import expect
import pytest

def test_cart_contains_expected_item(cart_page_with_item):
    """Verify that the expected item is in the cart."""
    expect(cart_page_with_item.get_item_locator("Sauce Labs Backpack")).to_be_visible()

def test_cart_after_remove_is_empty(cart_page_with_item):
    cart_page_with_item.remove_item("Sauce Labs Backpack")
    expect(cart_page_with_item.get_item_names_locator()).to_have_count(0)
