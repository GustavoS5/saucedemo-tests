# Saucedemo E2E Tests

End-to-end test suite for [saucedemo.com](https://www.saucedemo.com) — the
demo site by Sauce Labs — built with **Python**, **Playwright**, and
**pytest**, following the Page Object Model.

[![Playwright Tests](https://github.com/GustavoS5/saucedemo-tests/actions/workflows/playwright.yml/badge.svg)](https://github.com/<USER>/<REPO>/actions/workflows/playwright.yml)


## Tech stack

| Tool | Purpose |
| --- | --- |
| [Playwright](https://playwright.dev/python/) | Browser automation & web-first assertions |
| [pytest](https://docs.pytest.org/) | Test runner |
| [pytest-playwright](https://playwright.dev/python/docs/test-runners) | Playwright fixtures for pytest (`page`, `context`, `base_url`, …) |
| [pytest-xdist](https://pytest-xdist.readthedocs.io/) | Parallel test execution |
| [allure-pytest](https://allurereport.org/docs/pytest/) | Rich HTML test reports |
| [uv](https://docs.astral.sh/uv/) | Fast Python package manager |

## Project structure

```
.
├── .github/workflows/playwright.yml   # CI: push, PR, nightly
├── conftest.py                        # Shared fixtures (credentials, base url)
├── pages/                             # Page Object Model
│   ├── base_page.py                   # Minimal base: page + url + navigate()
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── tests/
│   ├── conftest.py                    # logged_in_page, inventory_page fixtures
│   ├── test_login.py
│   ├── test_inventory.py
│   ├── test_cart.py
│   └── test_checkout.py
└── pyproject.toml                     # Deps + pytest/Playwright config
```

## Test credentials

The suite uses saucedemo's publicly documented test account (`standard_user` /
`secret_sauce`) defined as constants in [`conftest.py`](conftest.py). Swap to
`locked_out_user`, `problem_user`, etc. in the page object methods to exercise
edge cases.

## Local setup

> Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
# 1. Install dependencies (creates a .venv automatically)
uv sync

# 2. Install the Playwright browser binaries
uv run playwright install chromium
```

## Running tests

```bash
# All tests
uv run pytest

# Only smoke tests
uv run pytest -m smoke

# Only end-to-end flow tests
uv run pytest -m e2e

# Run in parallel (pytest-xdist)
uv run pytest -n auto

# Headed mode for debugging
uv run pytest --headed

# A single test file
uv run pytest tests/test_login.py
```

### Test markers

| Marker | Meaning |
| --- | --- |
| `smoke`     | Fast core happy-path tests |
| `e2e`       | End-to-end user flow tests |
| `negative`  | Error and validation paths |

Apply with a decorator (`@pytest.mark.smoke`) or set `pytestmark` at the top
of a module.

## Debugging failed tests

The Playwright CLI flags are pre-configured in [`pyproject.toml`](pyproject.toml):

- `--tracing=retain-on-failure`
- `--screenshot=only-on-failure`
- `--video=retain-on-failure`

Artifacts for failing tests land in `test-results/`. Open a trace with:

```bash
uv run playwright show-trace test-results/<test-name>/trace.zip
```

## Allure reports

```bash
# Generate results and serve a live report
uv run pytest --alluredir=allure-results
uv run allure serve allure-results
```

## CI

Tests run automatically on every push, pull request, and nightly via the
[Playwright workflow](.github/workflows/playwright.yml). Failed test artifacts
(traces, screenshots, videos) are uploaded for 14 days.
