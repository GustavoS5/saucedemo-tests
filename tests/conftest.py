"""Test-level fixtures for the saucedemo suite."""

from __future__ import annotations

import pytest
from faker import Faker
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

# A fixed seed makes generated test data deterministic across runs and CI,
# which keeps failures reproducible without hard-coding static values.
FAKER_SEED = 42


@pytest.fixture
def faker() -> Faker:
    """A seeded Faker instance for generating realistic test data."""
    fake = Faker()
    Faker.seed(FAKER_SEED)
    return fake


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """A LoginPage object already loaded in the browser."""
    login = LoginPage(page)
    login.load()
    return login


@pytest.fixture
def logged_in_page(page: Page, saucedemo_credentials: dict[str, str]) -> Page:
    """A Playwright `page` already authenticated and on the inventory screen."""
    login = LoginPage(page)
    login.load()
    login.login(saucedemo_credentials["username"], saucedemo_credentials["password"])
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


@pytest.fixture
def checkout_page(cart_page_with_item: CartPage) -> CheckoutPage:
    """A CheckoutPage (step one) reached from a cart holding one item."""
    cart_page_with_item.go_to_checkout()
    return CheckoutPage(cart_page_with_item.page)


@pytest.fixture
def checkout_page_with_multiple_items(
    cart_page_with_multiple_items: CartPage,
) -> CheckoutPage:
    """A CheckoutPage (step one) reached from a cart holding multiple items."""
    cart_page_with_multiple_items.go_to_checkout()
    return CheckoutPage(cart_page_with_multiple_items.page)
