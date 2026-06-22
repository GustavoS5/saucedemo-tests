"""Login tests for the saucedemo site."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

# saucedemo always shows six products in the inventory list.
EXPECTED_INVENTORY_ITEM_COUNT = 6


@pytest.mark.smoke
def test_login_all_valid_users(
    login_page: LoginPage,
    valid_user: str,
    saucedemo_password: str,
    base_url: str,
):
    """Every saucedemo account in VALID_USERS should reach the inventory page."""
    login_page.login(valid_user, saucedemo_password)
    inventory = InventoryPage(login_page.page)
    expect(inventory.title).to_have_text("Products")
    expect(login_page.page).to_have_url(f"{base_url}/inventory.html")


@pytest.mark.smoke
def test_post_login_state(logged_in_page, base_url: str):
    """After login the URL, app logo, and inventory list are all present."""
    inventory = InventoryPage(logged_in_page)
    expect(inventory.title).to_have_text("Products")
    expect(logged_in_page).to_have_url(f"{base_url}/inventory.html")
    expect(logged_in_page.locator(".app_logo")).to_be_visible()
    expect(inventory.inventory_items).to_have_count(EXPECTED_INVENTORY_ITEM_COUNT)


def test_logout_flow(inventory_page: InventoryPage, base_url: str):
    """Opening the menu and clicking Logout returns to the login page."""
    inventory_page.logout()
    expect(inventory_page.page).to_have_url(f"{base_url}/")
    login = LoginPage(inventory_page.page)
    expect(login.username_input).to_be_visible()
    expect(login.login_button).to_be_visible()


@pytest.mark.parametrize(
    "username, password, expected_error",
    [
        pytest.param(
            "locked_out_user",
            "secret_sauce",
            "Epic sadface: Sorry, this user has been locked out.",
            id="locked_out_user",
        ),
        pytest.param(
            "",
            "secret_sauce",
            "Epic sadface: Username is required",
            id="empty_username",
        ),
        pytest.param(
            "standard_user",
            "",
            "Epic sadface: Password is required",
            id="empty_password",
        ),
        pytest.param(
            "standard_user",
            "wrong_password",
            "Epic sadface: Username and password do not match any user in this service",
            id="wrong_password",
        ),
        pytest.param(
            "",
            "",
            "Epic sadface: Username is required",
            id="empty_username_and_password",
        ),
    ],
)
@pytest.mark.negative
def test_login_errors(
    login_page: LoginPage, username, password, expected_error, base_url: str
):
    """Invalid login attempts keep the user on the login page with an error."""
    login_page.login(username, password)
    expect(login_page.page).to_have_url(f"{base_url}/")
    expect(login_page.error_message).to_contain_text(expected_error)
