# Saucedemo E2E Tests

End-to-end test suite for [saucedemo.com](https://www.saucedemo.com) — the
demo site by Sauce Labs — built with **Python**, **Playwright**, and
**pytest**, following the Page Object Model.

[![Playwright Tests](https://github.com/GustavoS5/saucedemo-tests/actions/workflows/playwright.yml/badge.svg)](https://github.com/GustavoS5/saucedemo-tests/actions/workflows/playwright.yml)

## Tech stack

| Tool                                                                 | Purpose                                                           |
|----------------------------------------------------------------------|-------------------------------------------------------------------|
| [Playwright](https://playwright.dev/python/)                         | Browser automation & web-first assertions                         |
| [pytest](https://docs.pytest.org/)                                   | Test runner                                                       |
| [pytest-playwright](https://playwright.dev/python/docs/test-runners) | Playwright fixtures for pytest (`page`, `context`, `base_url`, …) |
| [pytest-xdist](https://pytest-xdist.readthedocs.io/)                 | Parallel test execution                                           |
| [allure-pytest](https://allurereport.org/docs/pytest/)               | Rich HTML test reports                                            |
| [uv](https://docs.astral.sh/uv/)                                     | Fast Python package manager                                       |

## Project structure

```
.
├── .github/workflows/playwright.yml   # CI: push, PR, nightly
├── conftest.py                        # Shared fixtures (password, base url, test-id mapping)
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
│   └── test_edge_users.py             # Known defects in special demo accounts
├── pyproject.toml                     # Deps + pytest/Playwright config
└── uv.lock                            # Pinned dependency lockfile for reproducible installs
```

## Test credentials

The suite reads the shared saucedemo password from `SAUCEDEMO_PASSWORD`.
Most tests use `standard_user`. The root fixtures parametrize the supported
login accounts, while tests for intentionally defective accounts live in
`tests/test_edge_users.py`.
The `.env` file is gitignored — copy `.env.example` as your local
template. For CI, set `SAUCEDEMO_PASSWORD` as a GitHub Actions secret.

The password is committed in `.env.example` because saucedemo is a public demo
site with intentionally published credentials.

## Local setup

> Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
# macOS/Linux
# 1. Install dependencies (creates a .venv automatically)
uv sync

# 2. Install the Playwright browser binaries
uv run playwright install chromium

# 3. Create a local dotenv file from the template and set your password
cp .env.example .env
```

```powershell
# Windows (PowerShell)
# 1. Install dependencies (creates a .venv automatically)
uv sync

# 2. Install the Playwright browser binaries
uv run playwright install chromium

# 3. Create a local dotenv file from the template and set your password
copy .env.example .env
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

| Marker      | Meaning                                                        |
|-------------|----------------------------------------------------------------|
| `smoke`     | Fast core happy-path tests                                     |
| `e2e`       | End-to-end user flow tests                                     |
| `negative`  | Error and validation paths                                     |
| `known_bug` | Expected behavior currently blocked by a known SauceDemo defect |

## Known upstream defects

`tests/test_edge_users.py` covers two saucedemo accounts that are
intentionally buggy demo users:

- **`problem_user`** — every product image is swapped for the same 404
  placeholder graphic, sorting does not reorder the list correctly, and
  checkout fields do not retain their values independently.
- **`error_user`** — the checkout `lastName` field is wired to a handler
  that throws a JavaScript `TypeError` on input, so the value never
  registers and checkout can't complete normally.

These tests assert the behavior a working application should provide and are
marked `xfail(strict=False)`. A known defect is therefore reported as XFAIL
without hiding failures elsewhere. If SauceDemo fixes a defect, the
corresponding test reports XPASS so the marker can be reviewed and removed.

## Design decisions

- Page objects keep selectors and page-level actions separate from test
  intent. Shared UI such as the footer is represented as a component rather
  than duplicated across page objects.
- Locators prefer SauceDemo's `data-test` hooks. The project configures
  Playwright's test-id selector once, so tests avoid CSS classes tied to
  presentation.
- Function-scoped Playwright pages and fixtures give each test an isolated
  browser context. Higher-level fixtures build reusable states such as an
  authenticated inventory page or a cart containing known products.
- Known defects assert the desired behavior and use non-strict XFAIL markers.
  This documents upstream limitations while allowing CI to reveal when a
  defect has been fixed.
- Pull requests run the complete suite on Chromium for fast feedback.
  Pushes and nightly runs add Firefox and WebKit coverage.

## Debugging failed tests

The Playwright CLI flags are pre-configured in [`pyproject.toml`](pyproject.toml):

- `--base-url=https://www.saucedemo.com`
- `--tracing=retain-on-failure`
- `--screenshot=only-on-failure`
- `--video=retain-on-failure`

Artifacts for failing tests land in `test-results/`. Open a trace with:

```bash
uv run playwright show-trace test-results/<test-name>/trace.zip
```

## Allure reports

```bash
# Generate Allure result files
uv run pytest --alluredir=allure-results

# Serve them with a separately installed Allure CLI
allure serve allure-results
```

The report adapter is installed with the project. Viewing the report also
requires the separate
[Allure command-line tool](https://allurereport.org/docs/install/).

## CI

Tests run automatically via the [Playwright workflow](.github/workflows/playwright.yml):

- Pull requests run the full suite on Chromium.
- Pushes to `main`/`master` and nightly schedules run the full suite across
  Chromium, Firefox, and WebKit.
- Failed test artifacts (traces, screenshots, videos) and Allure results are
  uploaded per browser for 14 days.

## Docker

Run the entire suite in a container with no local Python, `uv`, or Playwright
install required. The image:

- is based on `python:3.13-slim-bookworm`;
- installs dependencies from the pinned [`uv.lock`](uv.lock) via `uv`;
- **runs as a non-root user** (`appuser`, default UID/GID `1001`) for better
  isolation; and
- bakes in a headless **Chromium** build by default (configurable — see below).

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (Engine 24+ or Docker Desktop)
- [Docker Compose v2](https://docs.docker.com/compose/install/) (bundled with
  modern Docker Desktop)

### Quick start

```bash
# 1. Provide the publicly documented SauceDemo test credential
cp .env.docker.example .env

# 2. Build the image
docker compose build

# 3. Run the full suite
docker compose run --rm pytest

# Smoke tests only
docker compose run --rm pytest -m smoke

# A single test file
docker compose run --rm pytest tests/test_login.py
```

Traces, screenshots, video, and Allure results are bind-mounted back to the
host under `test-results/` and `allure-results/`. The Compose service also
sets `shm_size: 2gb` for Chromium stability under parallel (`-n auto`) runs.

### Browser selection at build time (`PLAYWRIGHT_BROWSERS`)

The Dockerfile accepts a `PLAYWRIGHT_BROWSERS` build ARG (default `chromium`)
so you can choose what gets baked into the image without editing files. The
Compose service passes `chromium` by default in
[`docker-compose.yml`](docker-compose.yml).

```bash
# Build with all browsers to mirror the CI matrix
docker compose build --build-arg PLAYWRIGHT_BROWSERS="chromium firefox webkit"

# Then run a specific browser (the image must contain that browser)
docker compose run --rm pytest --browser firefox
```

### File ownership on Linux (non-root container)

The container runs as `appuser` (default UID/GID `1001`). On Docker Desktop
(macOS/Windows) bind-mounted artifact directories work transparently. On
**Linux**, if `test-results/`/`allure-results/` end up owned by `root`,
rebuild matching your host user:

```bash
docker compose build --build-arg APP_UID="$(id -u)" --build-arg APP_GID="$(id -g)"
```

…or pre-create the dirs as your user (`mkdir -p test-results allure-results`).

### Plain Docker (without compose)

```bash
# Build (default: chromium only)
docker build -t saucedemo-tests .

# Run the smoke suite, forward the password from your shell
docker run --rm \
  -e SAUCEDEMO_PASSWORD="$SAUCEDEMO_PASSWORD" \
  --shm-size=2gb \
  -v "$(pwd)/test-results:/app/test-results" \
  -v "$(pwd)/allure-results:/app/allure-results" \
  saucedemo-tests -m smoke -n auto
```

> On Windows PowerShell, replace `$(pwd)` with `${PWD}` and remove the
> backslash line continuations.
