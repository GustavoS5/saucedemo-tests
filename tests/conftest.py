"""Test-level fixtures for the saucedemo suite."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """A LoginPage object already loaded in the browser."""
    login = LoginPage(page)
    login.load()
    return login


@pytest.fixture
def logged_in_page(
        page: Page, saucedemo_credentials: dict[str, str]
) -> Page:
    """A Playwright `page` already authenticated and on the inventory screen."""
    login = LoginPage(page)
    login.load()
    login.login(
        saucedemo_credentials["username"], saucedemo_credentials["password"]
    )
    return page


@pytest.fixture
def inventory_page(logged_in_page: Page) -> InventoryPage:
    """An InventoryPage object bound to an authenticated session."""
    return InventoryPage(logged_in_page)


@pytest.fixture
def cart_page_with_item(inventory_page: InventoryPage) -> CartPage:
    """A CartPage with one known item already added."""
    inventory_page.add_item_to_cart("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    return CartPage(inventory_page.page)


@pytest.fixture
def cart_page_with_multiple_items(inventory_page: InventoryPage) -> CartPage:
    """A CartPage with multiple known items already added."""
    inventory_page.add_item_to_cart("Sauce Labs Backpack")
    inventory_page.add_item_to_cart("Sauce Labs Bolt T-Shirt")
    inventory_page.add_item_to_cart("Sauce Labs Onesie")
    inventory_page.go_to_cart()
    return CartPage(inventory_page.page)
