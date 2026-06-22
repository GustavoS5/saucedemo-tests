"""Project-level pytest fixtures and configuration."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

# Load local-only environment variables from .env when present. CI injects these
# values directly via GitHub Actions secrets.
load_dotenv()

# Saucedemo credentials come from environment variables to avoid hard-coding
# them in test source (see .env.example for the template).
CREDENTIAL_ENV_VARS = {
    "username": "SAUCEDEMO_USERNAME",
    "password": "SAUCEDEMO_PASSWORD",
}

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
    credentials = {
        field: os.environ.get(env_var) for field, env_var in CREDENTIAL_ENV_VARS.items()
    }
    missing = [
        env_var
        for field, env_var in CREDENTIAL_ENV_VARS.items()
        if not credentials[field]
    ]

    if missing:
        raise RuntimeError(f"Set {', '.join(missing)} before running tests.")

    return {field: value for field, value in credentials.items() if value is not None}


@pytest.fixture(params=VALID_USERS, ids=VALID_USERS)
def valid_user(request) -> str:
    """Parametrized fixture yielding each saucedemo username that can log in."""
    return str(request.param)


@pytest.fixture(autouse=True)
def _configure_test_id_attribute(playwright) -> None:
    """Map `get_by_test_id()` to saucedemo's `data-test` attribute."""
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
