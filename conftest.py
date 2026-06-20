"""Project-level pytest fixtures and configuration.

These fixtures live at the repository root so they are available to every
test package. They intentionally stay minimal — the heavy lifting (browser
launch, context, page isolation, tracing, screenshots, retries) is handled
by the pytest-playwright plugin and the CLI flags declared in pyproject.toml.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

# Public saucedemo test credentials.
USERNAME = "standard_user"
PASSWORD = "secret_sauce"

# saucedemo exposes its stable hooks on `data-test` (with a hyphen), not the
# Playwright default `data-testid`. Set this once so every page object's
# `get_by_test_id()` call resolves to the right attribute.
TEST_ID_ATTRIBUTE = "data-test"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the site under test.

    Mirrors the `--base-url` flag from pyproject.toml so page objects can use
    `page.goto("/inventory.html")` with relative paths. Centralising it here
    keeps the target in one place if you ever point tests elsewhere.
    """
    return "https://www.saucedemo.com"


@pytest.fixture
def saucedemo_credentials() -> dict[str, str]:
    """Saucedemo login credentials as a {username, password} dict.

    Uses the well-known standard_user account. Request this fixture in tests
    that need to log in with the standard credentials.
    """
    return {"username": USERNAME, "password": PASSWORD}


@pytest.fixture(autouse=True)
def _configure_test_id_attribute(playwright) -> None:
    """Map `get_by_test_id()` to saucedemo's `data-test` attribute.

    Playwright defaults `get_by_test_id()` to `data-testid`, but saucedemo marks
    elements with `data-test` (hyphen). Without this, every `get_by_test_id()`
    locator across the page objects resolves to zero elements. This is a
    process-global setting, so a session-scoped autouse fixture is sufficient.
    """
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
