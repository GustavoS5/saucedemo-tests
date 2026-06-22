"""Checkout flow tests for the saucedemo site."""

from __future__ import annotations

import pytest
from faker import Faker
from playwright.sync_api import expect

from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage


def make_customer(faker: Faker) -> dict[str, str]:
    """Return a realistic customer info dict for checkout step one."""
    return {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "postal_code": faker.postcode(),
    }


@pytest.mark.smoke
def test_checkout_displays_step_one_title(checkout_page: CheckoutPage):
    """Reaching checkout step one shows the 'Your Information' title."""
    expect(checkout_page.title).to_have_text("Checkout: Your Information")


def test_cancel_checkout_returns_to_cart(checkout_page: CheckoutPage, base_url: str):
    """The 'Cancel' button on step one returns the user to the cart."""
    checkout_page.cancel_button.click()
    expect(checkout_page.page).to_have_url(f"{base_url}/cart.html")


@pytest.mark.parametrize(
    "missing_field, expected_error",
    [
        pytest.param(
            "first_name",
            "Error: First Name is required",
            id="missing_first_name",
        ),
        pytest.param(
            "last_name",
            "Error: Last Name is required",
            id="missing_last_name",
        ),
        pytest.param(
            "postal_code",
            "Error: Postal Code is required",
            id="missing_postal_code",
        ),
    ],
)
@pytest.mark.negative
def test_checkout_step_one_validation_errors(
    checkout_page: CheckoutPage,
    faker: Faker,
    missing_field: str,
    expected_error: str,
    base_url: str,
):
    """Submitting incomplete customer info keeps the user on step one."""
    customer = make_customer(faker)
    customer[missing_field] = ""

    checkout_page.fill_customer_info(
        customer["first_name"],
        customer["last_name"],
        customer["postal_code"],
    )
    checkout_page.continue_to_overview()

    expect(checkout_page.page).to_have_url(f"{base_url}/checkout-step-one.html")
    expect(checkout_page.error_message).to_contain_text(expected_error)


def test_complete_step_one_reaches_overview(
    checkout_page: CheckoutPage, faker: Faker, base_url: str
):
    """Valid customer info advances the user to the order overview."""
    customer = make_customer(faker)
    checkout_page.fill_customer_info(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )
    checkout_page.continue_to_overview()

    expect(checkout_page.page).to_have_url(f"{base_url}/checkout-step-two.html")
    expect(checkout_page.title).to_have_text("Checkout: Overview")


def test_overview_displays_summary_item(checkout_page: CheckoutPage, faker: Faker):
    """The order overview lists the item that was in the cart."""
    customer = make_customer(faker)
    checkout_page.fill_customer_info(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )
    checkout_page.continue_to_overview()

    expect(checkout_page.summary_items.first).to_be_visible()


def test_overview_shows_all_items(
    checkout_page_with_multiple_items: CheckoutPage, faker: Faker
):
    """The overview summary lists every item that was carried into checkout."""
    customer = make_customer(faker)
    checkout_page_with_multiple_items.fill_customer_info(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )
    checkout_page_with_multiple_items.continue_to_overview()

    expect(checkout_page_with_multiple_items.summary_items).to_have_count(3)


def test_cancel_from_overview_returns_to_inventory(
    checkout_page: CheckoutPage, faker: Faker, base_url: str
):
    """Cancelling from the order overview returns the user to the inventory."""
    customer = make_customer(faker)
    checkout_page.fill_customer_info(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )
    checkout_page.continue_to_overview()

    # Step two reuses the same `cancel` data-test hook as step one.
    checkout_page.cancel_button.click()
    expect(checkout_page.page).to_have_url(f"{base_url}/inventory.html")


@pytest.mark.e2e
def test_finish_order_reaches_confirmation(
    checkout_page: CheckoutPage, faker: Faker, base_url: str
):
    """Submitting the order reaches the confirmation screen."""
    customer = make_customer(faker)
    checkout_page.fill_customer_info(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )
    checkout_page.continue_to_overview()
    checkout_page.complete_order()

    expect(checkout_page.page).to_have_url(f"{base_url}/checkout-complete.html")
    expect(checkout_page.title).to_have_text("Checkout: Complete!")
    expect(checkout_page.complete_header).to_have_text("Thank you for your order!")


@pytest.mark.e2e
def test_full_checkout_flow_empties_cart(
    checkout_page: CheckoutPage, faker: Faker, base_url: str
):
    """After a completed order the shopping cart badge is gone."""
    customer = make_customer(faker)
    checkout_page.fill_customer_info(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )
    checkout_page.continue_to_overview()
    checkout_page.complete_order()

    inventory = InventoryPage(checkout_page.page)
    expect(inventory.shopping_cart_badge).to_be_hidden()


@pytest.mark.e2e
def test_full_checkout_flow_with_multiple_items(
    checkout_page_with_multiple_items: CheckoutPage,
    faker: Faker,
    base_url: str,
):
    """A full cart of items can be checked out end to end."""
    customer = make_customer(faker)
    checkout_page_with_multiple_items.fill_customer_info(
        customer["first_name"], customer["last_name"], customer["postal_code"]
    )
    checkout_page_with_multiple_items.continue_to_overview()
    expect(checkout_page_with_multiple_items.summary_items).to_have_count(3)

    checkout_page_with_multiple_items.complete_order()
    expect(checkout_page_with_multiple_items.page).to_have_url(
        f"{base_url}/checkout-complete.html"
    )
    expect(checkout_page_with_multiple_items.complete_header).to_be_visible()
