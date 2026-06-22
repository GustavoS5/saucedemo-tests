"""Edge-case tests for saucedemo's special problem/error users.

These users exhibit intentionally broken behaviour that should be asserted
so regressions in the demo site are caught:

- ``problem_user``: inventory item images are replaced by a 404 placeholder,
  checkout form fields are wired incorrectly, and sorting is broken.
- ``error_user``  : checkout form interactions throw JavaScript errors.
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def login_as_user(page, username: str, password: str) -> InventoryPage:
    """Log in as a saucedemo user and return the inventory page object."""
    login = LoginPage(page)
    login.load()
    login.login(username, password)
    return InventoryPage(page)


@pytest.fixture
def checkout_for_user(page, saucedemo_credentials):
    """Factory fixture that reaches checkout step one for a given username."""

    def _checkout_for_user(username: str, item_name: str = "Sauce Labs Backpack"):
        inventory = login_as_user(page, username, saucedemo_credentials["password"])
        inventory.add_item_to_cart(item_name)
        inventory.go_to_cart()

        cart = CartPage(page)
        cart.go_to_checkout()
        return CheckoutPage(page)

    return _checkout_for_user


@pytest.fixture
def problem_user_inventory(page, saucedemo_credentials):
    """A logged-in ``problem_user`` session on the inventory page."""
    return login_as_user(page, "problem_user", saucedemo_credentials["password"])


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


def test_problem_user_images_are_placeholder(problem_user_inventory):
    """Every inventory image is the 404/placeholder graphic, not the product."""
    imgs = problem_user_inventory.page.locator('[data-test="inventory-item"] img')
    expect(imgs).not_to_have_count(0)

    for i in range(imgs.count()):
        expect(imgs.nth(i)).to_have_attribute("src", re.compile("sl-404"))


def test_problem_user_all_images_identical(problem_user_inventory):
    """All inventory images share the same (broken) source URL."""
    imgs = problem_user_inventory.page.locator('[data-test="inventory-item"] img')
    expect(imgs).not_to_have_count(0)

    first_src = imgs.first.get_attribute("src")
    for i in range(imgs.count()):
        expect(imgs.nth(i)).to_have_attribute("src", first_src)


# --- problem_user: broken sorting ----------------------------------------


def test_problem_user_sort_price_low_to_high_broken(problem_user_inventory):
    """Sorting by price (low to high) does not actually reorder items."""
    problem_user_inventory.sort_by("lohi")
    prices = problem_user_inventory.get_item_prices_in_order()
    assert prices != sorted(prices), (
        f"Expected broken sorting (unsorted prices), but got {prices}"
    )


def test_problem_user_sort_name_descending_broken(problem_user_inventory):
    """Sorting by name (Z to A) does not reorder items for problem_user."""
    problem_user_inventory.sort_by("za")
    names = problem_user_inventory.get_item_names_in_order()
    assert names != sorted(names, reverse=True), (
        f"Expected broken sorting (not reverse-alpha), but got {names}"
    )


# --- problem_user: checkout form fields misaligned ------------------------


def test_problem_user_checkout_form_fields_misaligned(problem_user_checkout, page):
    """Filling lastName overwrites firstName — fields are wired incorrectly."""
    checkout = problem_user_checkout

    checkout.first_name_input.fill("Alpha")
    expect(page.get_by_test_id("firstName")).to_have_value("Alpha")

    checkout.last_name_input.fill("Beta")

    first_val = page.get_by_test_id("firstName").input_value()
    last_val = page.get_by_test_id("lastName").input_value()

    assert (first_val, last_val) != ("Alpha", "Beta"), (
        f"Expected misaligned form fields, but got firstName='{first_val}', "
        f"lastName='{last_val}' — fields appear to work correctly"
    )


def test_problem_user_checkout_cannot_complete_normally(
        problem_user_checkout, page, base_url: str
):
    """Checkout step one cannot be completed normally as problem_user."""
    checkout = problem_user_checkout

    checkout.first_name_input.fill("Test")
    checkout.last_name_input.fill("User")
    checkout.postal_code_input.fill("12345")

    values = {
        "firstName": page.get_by_test_id("firstName").input_value(),
        "lastName": page.get_by_test_id("lastName").input_value(),
        "postalCode": page.get_by_test_id("postalCode").input_value(),
    }

    assert values != {
        "firstName": "Test",
        "lastName": "User",
        "postalCode": "12345",
    }, (
        f"All form fields accepted input correctly ({values}), "
        "but problem_user should have at least one misaligned field"
    )


# --- error_user: JavaScript errors + broken checkout field ----------------


def test_error_user_can_log_in(page, saucedemo_credentials, base_url: str):
    """error_user authenticates and lands on inventory."""
    inventory = login_as_user(page, "error_user", saucedemo_credentials["password"])
    expect(inventory.title).to_have_text("Products")
    expect(page).to_have_url(f"{base_url}/inventory.html")


def test_error_user_can_add_items_to_cart(page, saucedemo_credentials, base_url: str):
    """error_user can add items to the cart on the inventory page."""
    inventory = login_as_user(page, "error_user", saucedemo_credentials["password"])
    inventory.add_item_to_cart("Sauce Labs Backpack")
    inventory.add_item_to_cart("Sauce Labs Bike Light")
    expect(inventory.shopping_cart_badge).to_have_text("2")


def test_error_user_checkout_reaches_step_one(error_user_checkout, base_url: str):
    """error_user can reach checkout step one."""
    expect(error_user_checkout.page).to_have_url(f"{base_url}/checkout-step-one.html")
    expect(error_user_checkout.title).to_have_text("Checkout: Your Information")


def test_error_user_lastname_field_broken(error_user_checkout, page):
    """The lastName field does not capture input for error_user.

    Filling lastName triggers a JS TypeError in the onChange handler
    (Cannot read properties of undefined), so the value never registers.
    """
    checkout = error_user_checkout

    checkout.first_name_input.fill("Test")
    checkout.postal_code_input.fill("12345")
    expect(page.get_by_test_id("firstName")).to_have_value("Test")
    expect(page.get_by_test_id("postalCode")).to_have_value("12345")

    checkout.last_name_input.fill("User")
    expect(page.get_by_test_id("lastName")).not_to_have_value("User")


def test_error_user_lastname_onchange_throws_js_error(error_user_checkout, page):
    """Typing into the lastName field triggers a JavaScript TypeError.

    error_user's checkout form has a broken onChange handler on lastName.
    This is caught as an uncaught page error (pageerror), confirming the
    field's event handler is misconfigured.
    """

    with page.expect_event("pageerror", timeout=5000) as event_info:
        page.get_by_test_id("lastName").type("Trigger")

    error = event_info.value
    assert "TypeError" in str(error) or "undefined" in str(error), (
        f"Expected a TypeError in page errors, got: {error}"
    )


def test_error_user_cannot_complete_checkout(error_user_checkout, page, base_url: str):
    """error_user cannot finish an order — the Finish button fails.

    Step one proceeds to step two (validation doesn't block the empty
    lastName), but clicking Finish on the overview does not advance to
    the confirmation page. The order cannot be completed. This documents
    the actual observed behaviour in the current saucedemo build.
    """
    checkout = error_user_checkout

    checkout.first_name_input.fill("Test")
    checkout.last_name_input.fill("Ignored")
    checkout.postal_code_input.fill("12345")

    checkout.continue_to_overview()
    expect(page).to_have_url(f"{base_url}/checkout-step-two.html")

    checkout.complete_order()
    expect(page).to_have_url(f"{base_url}/checkout-step-two.html")
    expect(checkout.complete_header).not_to_be_visible()


def test_error_user_remove_item_from_cart(page, saucedemo_credentials, base_url: str):
    """error_user can remove items from the cart (no remove bug in this build).

    Earlier saucedemo versions had a remove-button bug for error_user, but the
    current version handles removal correctly. This test documents that and
    will fail (alerting us) if the bug reappears in a future build.
    """
    inventory = login_as_user(page, "error_user", saucedemo_credentials["password"])
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
