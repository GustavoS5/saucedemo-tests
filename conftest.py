"""Project-level pytest fixtures and configuration."""

from __future__ import annotations

import pytest

# Public saucedemo test credentials.
USERNAME = "standard_user"
PASSWORD = "secret_sauce"

# All saucedemo accounts that successfully authenticate. `locked_out_user`
# is intentionally excluded — it is an error-path fixture, not a happy path.
VALID_USERS = (
    "standard_user",
    "problem_user",
    "performance_glitch_user",
    "error_user",
    "visual_user",
)

# saucedemo exposes its stable hooks on `data-test` (with a hyphen), not the
# Playwright default `data-testid`.
TEST_ID_ATTRIBUTE = "data-test"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the site under test."""
    return "https://www.saucedemo.com"


@pytest.fixture
def saucedemo_credentials() -> dict[str, str]:
    """Saucedemo login credentials as a {username, password} dict."""
    return {"username": USERNAME, "password": PASSWORD}


@pytest.fixture(params=VALID_USERS, ids=VALID_USERS)
def valid_user(request) -> str:
    """Parametrized fixture yielding each saucedemo username that can log in."""
    return request.param


@pytest.fixture(autouse=True)
def _configure_test_id_attribute(playwright) -> None:
    """Map `get_by_test_id()` to saucedemo's `data-test` attribute."""
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
