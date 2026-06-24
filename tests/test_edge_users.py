"""Edge-case tests for problem_user and error_user broken behaviour."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

KNOWN_BUG = pytest.mark.xfail(
    reason="Documents intentionally broken behaviour in the upstream SauceDemo app",
    strict=False,
)


def login_as_user(page, username: str, password: str) -> InventoryPage:
    """Log in as a saucedemo user and return the inventory page object."""
    login = LoginPage(page)
    login.load()
    login.login(username, password)
    return InventoryPage(page)


@pytest.fixture
def checkout_for_user(page, saucedemo_password):
    """Factory fixture that reaches checkout step one for a given username."""

    def _checkout_for_user(username: str, item_name: str = "Sauce Labs Backpack"):
        inventory = login_as_user(page, username, saucedemo_password)
        inventory.add_item_to_cart(item_name)
        inventory.go_to_cart()

        cart = CartPage(page)
        cart.go_to_checkout()
        return CheckoutPage(page)

    return _checkout_for_user


@pytest.fixture
def problem_user_inventory(page, saucedemo_password):
    """A logged-in ``problem_user`` session on the inventory page."""
    return login_as_user(page, "problem_user", saucedemo_password)


@pytest.fixture
def problem_user_checkout(checkout_for_user):
    """A ``problem_user`` session with one item at checkout step one."""
    return checkout_for_user("problem_user")


@pytest.fixture
def error_user_checkout(checkout_for_user):
    """An ``error_user`` session with one item at checkout step one."""
    return checkout_for_user("error_user")


# --- problem_user: broken images ------------------------------------------


def test_problem_user_inventory_loads(problem_user_inventory, base_url: str):
    """The problem_user still reaches the inventory page."""
    expect(problem_user_inventory.page).to_have_url(f"{base_url}/inventory.html")
    expect(problem_user_inventory.title).to_have_text("Products")


@pytest.mark.known_bug
@KNOWN_BUG
def test_problem_user_images_are_valid(problem_user_inventory):
    """Inventory images should use real product graphics, not placeholders."""
    imgs = problem_user_inventory.page.locator('[data-test="inventory-item"] img')
    expect(imgs).not_to_have_count(0)

    for i in range(imgs.count()):
        expect(imgs.nth(i)).not_to_have_attribute("src", re.compile("sl-404"))


@pytest.mark.known_bug
@KNOWN_BUG
def test_problem_user_images_are_product_specific(problem_user_inventory):
    """Inventory products should not all display the same image."""
    imgs = problem_user_inventory.page.locator('[data-test="inventory-item"] img')
    expect(imgs).not_to_have_count(0)

    sources = [imgs.nth(i).get_attribute("src") for i in range(imgs.count())]
    assert len(set(sources)) == imgs.count()


# --- problem_user: broken sorting ----------------------------------------


@pytest.mark.known_bug
@KNOWN_BUG
def test_problem_user_sorts_price_low_to_high(problem_user_inventory):
    """Sorting by price should reorder products from low to high."""
    problem_user_inventory.sort_by("lohi")
    prices = problem_user_inventory.get_item_prices_in_order()
    assert prices == sorted(prices), f"Prices were not sorted low to high: {prices}"


@pytest.mark.known_bug
@KNOWN_BUG
def test_problem_user_sorts_name_descending(problem_user_inventory):
    """Sorting by name should reorder products from Z to A."""
    problem_user_inventory.sort_by("za")
    names = problem_user_inventory.get_item_names_in_order()
    assert names == sorted(names, reverse=True), (
        f"Names were not sorted from Z to A: {names}"
    )


# --- problem_user: checkout form fields misaligned ------------------------


@pytest.mark.known_bug
@KNOWN_BUG
def test_problem_user_checkout_fields_accept_input(problem_user_checkout, page):
    """Checkout fields should independently retain their entered values."""
    checkout = problem_user_checkout

    checkout.first_name_input.fill("Alpha")
    expect(page.get_by_test_id("firstName")).to_have_value("Alpha")

    checkout.last_name_input.fill("Beta")

    first_val = page.get_by_test_id("firstName").input_value()
    last_val = page.get_by_test_id("lastName").input_value()

    assert (first_val, last_val) == ("Alpha", "Beta")


@pytest.mark.known_bug
@KNOWN_BUG
def test_problem_user_checkout_accepts_customer_info(
    problem_user_checkout, page, base_url: str
):
    """Valid customer information should advance checkout to the overview."""
    checkout = problem_user_checkout

    checkout.first_name_input.fill("Test")
    checkout.last_name_input.fill("User")
    checkout.postal_code_input.fill("12345")

    checkout.continue_to_overview()
    expect(page).to_have_url(f"{base_url}/checkout-step-two.html")


# --- error_user: JavaScript errors + broken checkout field ----------------


def test_error_user_can_log_in(page, saucedemo_password, base_url: str):
    """error_user authenticates and lands on inventory."""
    inventory = login_as_user(page, "error_user", saucedemo_password)
    expect(inventory.title).to_have_text("Products")
    expect(page).to_have_url(f"{base_url}/inventory.html")


def test_error_user_can_add_items_to_cart(page, saucedemo_password, base_url: str):
    """error_user can add items to the cart on the inventory page."""
    inventory = login_as_user(page, "error_user", saucedemo_password)
    inventory.add_item_to_cart("Sauce Labs Backpack")
    inventory.add_item_to_cart("Sauce Labs Bike Light")
    expect(inventory.shopping_cart_badge).to_have_text("2")


def test_error_user_checkout_reaches_step_one(error_user_checkout, base_url: str):
    """error_user can reach checkout step one."""
    expect(error_user_checkout.page).to_have_url(f"{base_url}/checkout-step-one.html")
    expect(error_user_checkout.title).to_have_text("Checkout: Your Information")


@pytest.mark.known_bug
@KNOWN_BUG
def test_error_user_lastname_field_accepts_input(error_user_checkout, page):
    """The last-name field should retain normally entered input."""
    checkout = error_user_checkout

    checkout.first_name_input.fill("Test")
    checkout.postal_code_input.fill("12345")
    expect(page.get_by_test_id("firstName")).to_have_value("Test")
    expect(page.get_by_test_id("postalCode")).to_have_value("12345")

    checkout.last_name_input.fill("User")
    expect(page.get_by_test_id("lastName")).to_have_value("User")


@pytest.mark.known_bug
@KNOWN_BUG
def test_error_user_lastname_change_has_no_js_error(error_user_checkout, page):
    """Typing into lastName should not trigger an unhandled JavaScript error."""
    page_errors = []
    page.on("pageerror", page_errors.append)

    page.get_by_test_id("lastName").press_sequentially("Trigger")

    expect(page.get_by_test_id("lastName")).to_have_value("Trigger")
    assert not page_errors, f"Unexpected page errors: {page_errors}"


@pytest.mark.known_bug
@KNOWN_BUG
def test_error_user_can_complete_checkout(error_user_checkout, page, base_url: str):
    """A valid order should reach the checkout confirmation screen."""
    checkout = error_user_checkout

    checkout.first_name_input.fill("Test")
    checkout.last_name_input.fill("Ignored")
    checkout.postal_code_input.fill("12345")

    checkout.continue_to_overview()
    expect(page).to_have_url(f"{base_url}/checkout-step-two.html")

    checkout.complete_order()
    expect(page).to_have_url(f"{base_url}/checkout-complete.html")
    expect(checkout.complete_header).to_have_text("Thank you for your order!")


def test_error_user_remove_item_from_cart(page, saucedemo_password, base_url: str):
    """error_user can remove items from the cart."""
    inventory = login_as_user(page, "error_user", saucedemo_password)
    inventory.add_item_to_cart("Sauce Labs Backpack")
    inventory.add_item_to_cart("Sauce Labs Bike Light")
    inventory.go_to_cart()

    cart = CartPage(page)
    expect(cart.get_item_names_locator()).to_have_count(2)

    cart.remove_item("Sauce Labs Bike Light")
    expect(cart.get_item_names_locator()).to_have_count(1)
    expect(
        cart.cart_items.filter(
            has=page.get_by_test_id("inventory-item-name").filter(
                has_text="Sauce Labs Backpack"
            )
        )
    ).to_be_visible()
