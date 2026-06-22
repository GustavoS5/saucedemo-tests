# Saucedemo E2E Tests

End-to-end test suite for [saucedemo.com](https://www.saucedemo.com) — the
demo site by Sauce Labs — built with **Python**, **Playwright**, and
**pytest**, following the Page Object Model.

[![Playwright Tests](https://github.com/GustavoS5/saucedemo-tests/actions/workflows/playwright.yml/badge.svg)](https://github.com/GustavoS5/saucedemo-tests/actions/workflows/playwright.yml)


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
├── conftest.py                        # Shared fixtures (credentials, base url, test-id mapping)
├── pages/                             # Page Object Model
│   ├── __init__.py
│   ├── base_page.py                   # Minimal base: page + url + navigate()
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   ├── checkout_page.py
│   ├── product_detail_page.py
│   └── footer_component.py            # Shared footer component
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # logged_in_page, inventory_page, cart, checkout fixtures
│   ├── test_login.py
│   ├── test_inventory.py
│   ├── test_cart.py
│   ├── test_cart_persistence.py
│   ├── test_checkout.py
│   ├── test_product_detail.py
│   ├── test_sorting.py
│   ├── test_footer.py                 # Shared footer component tests
│   └── test_edge_users.py             # problem_user / error_user broken behaviour
├── pyproject.toml                     # Deps + pytest/Playwright config
└── uv.lock                            # Pinned dependency lockfile for reproducible installs
```

## Test credentials

The suite reads saucedemo credentials from environment variables so credentials
are not hard-coded in the test code:

| Variable | Example value |
| --- | --- |
| `SAUCEDEMO_USERNAME` | `standard_user` |
| `SAUCEDEMO_PASSWORD` | `secret_sauce` |

The password is included in `.env.example` because Saucedemo is a public demo
site and these credentials are intentionally published for test automation
practice. For a real application, never commit usable credentials; keep only
placeholders in committed templates and inject real values via a secret manager
or CI secrets.

For local runs, `python-dotenv` loads these values from a local `.env` file when
one is present. The `.env` file is ignored by Git; commit only `.env.example` as
the safe template.

For CI, configure these values as GitHub Actions secrets. The edge-user tests
still swap usernames such as `problem_user` and `error_user` while reusing the
injected password.

## Local setup

> Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```powershell
# 1. Install dependencies (creates a .venv automatically)
uv sync

# 2. Install the Playwright browser binaries
uv run playwright install chromium

# 3. Create a local dotenv file from the committed template
copy .env.example .env

# 4. Review .env; the template already contains Saucedemo's public demo credentials
#    SAUCEDEMO_USERNAME=standard_user
#    SAUCEDEMO_PASSWORD=secret_sauce
```

Alternatively, you can skip `.env` and export the same variables into the current
shell session before running tests.

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

Tests run automatically via the [Playwright workflow](.github/workflows/playwright.yml):

- Pull requests run the smoke suite across Chromium, Firefox, and WebKit.
- Pushes to `main`/`master` and nightly schedules run the full suite across
  Chromium, Firefox, and WebKit.
- Failed test artifacts (traces, screenshots, videos) and Allure results are
  uploaded per browser for 14 days.
