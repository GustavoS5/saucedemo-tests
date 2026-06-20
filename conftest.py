"""Project-level pytest fixtures and configuration.

These fixtures live at the repository root so they are available to every
test package. They intentionally stay minimal — the heavy lifting (browser
launch, context, page isolation, tracing, screenshots, retries) is handled
by the pytest-playwright plugin and the CLI flags declared in pyproject.toml.
"""

from __future__ import annotations

import pytest

# Public saucedemo test credentials.
USERNAME = "standard_user"
PASSWORD = "secret_sauce"


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
