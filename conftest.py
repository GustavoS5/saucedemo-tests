"""Project-level pytest fixtures and configuration."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

# Loads SAUCEDEMO_PASSWORD from a local .env file when present.
load_dotenv()


# `locked_out_user` is intentionally excluded — error-path fixture.
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


@pytest.fixture
def saucedemo_password() -> str:
    """The shared saucedemo password, read from SAUCEDEMO_PASSWORD."""
    password = os.environ.get("SAUCEDEMO_PASSWORD", "").strip()

    if not password:
        raise RuntimeError(
            "Set SAUCEDEMO_PASSWORD environment variable before running tests."
        )

    return password


@pytest.fixture(params=VALID_USERS, ids=VALID_USERS)
def valid_user(request) -> str:
    """Parametrized fixture yielding each saucedemo username that can log in."""
    return str(request.param)


@pytest.fixture(autouse=True)
def _configure_test_id_attribute(playwright) -> None:
    """Map `get_by_test_id()` to saucedemo's `data-test` attribute."""
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
