"""Login tests for the saucedemo site."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def test_login_valid_credentials(saucedemo_credentials, login_page: LoginPage):
    """Test that a user can log in with valid credentials."""
    login_page.login(
        saucedemo_credentials["username"], saucedemo_credentials["password"]
    )
    inventory = InventoryPage(login_page.page)
    expect(inventory.title).to_have_text("Products")
