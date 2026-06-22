"""Product detail page tests for the saucedemo site."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from pages.product_detail_page import ProductDetailPage


def test_open_product_detail_page(inventory_page, base_url: str):
    """Clicking a product name navigates to its detail screen."""
    inventory_page.open_item("Sauce Labs Backpack")
    expect(inventory_page.page).to_have_url(
        re.compile(re.escape(f"{base_url}/inventory-item.html") + r"\?id=\d+")
    )


def test_product_detail_shows_correct_name(inventory_page):
    """The detail page shows the name of the product that was opened."""
    inventory_page.open_item("Sauce Labs Backpack")
    detail = ProductDetailPage(inventory_page.page)
    expect(detail.item_name).to_have_text("Sauce Labs Backpack")


def test_product_detail_shows_price(inventory_page):
    """The detail page shows a non-empty price matching inventory."""
    item_name = "Sauce Labs Backpack"
    inventory_price = inventory_page.get_item_price(item_name)

    inventory_page.open_item(item_name)
    detail = ProductDetailPage(inventory_page.page)
    expect(detail.item_price).to_have_text(inventory_price)


def test_product_detail_shows_description(inventory_page):
    """The detail page shows a non-empty description."""
    inventory_page.open_item("Sauce Labs Backpack")
    detail = ProductDetailPage(inventory_page.page)
    expect(detail.item_desc).not_to_be_empty()


def test_add_to_cart_from_detail_page(inventory_page):
    """Adding an item from its detail page updates the cart badge."""
    inventory_page.open_item("Sauce Labs Backpack")
    detail = ProductDetailPage(inventory_page.page)
    detail.add_to_cart()
    expect(inventory_page.shopping_cart_badge).to_have_text("1")


@pytest.mark.parametrize(
    "item_name",
    [
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Fleece Jacket",
    ],
)
def test_detail_price_matches_inventory(inventory_page, item_name):
    """The price on the detail page matches the price on the inventory list."""
    inventory_price = inventory_page.get_item_price(item_name)
    inventory_page.open_item(item_name)

    detail = ProductDetailPage(inventory_page.page)
    expect(detail.item_price).to_have_text(inventory_price)


def test_back_to_products_returns_to_inventory(inventory_page, base_url: str):
    """The 'Back to products' button returns to the inventory list."""
    inventory_page.open_item("Sauce Labs Backpack")
    detail = ProductDetailPage(inventory_page.page)
    detail.go_back_to_products()

    expect(inventory_page.page).to_have_url(f"{base_url}/inventory.html")
