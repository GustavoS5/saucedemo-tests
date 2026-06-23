# syntax=docker/dockerfile:1
#
# Containerized version of the saucedemo E2E test suite
# (Python 3.13 + Playwright + pytest, managed with uv).
#
# Build:  docker build -t saucedemo-tests .
# Run:    docker run --rm -e SAUCEDEMO_PASSWORD="$SAUCEDEMO_PASSWORD" \
#           -v "$(pwd)/test-results:/app/test-results" \
#           -v "$(pwd)/allure-results:/app/allure-results" \
#           saucedemo-tests -m smoke -n auto
#
# The entrypoint is `pytest`, so any args after the image name
# are forwarded to pytest (markers, -n, file paths, ...).
FROM python:3.13-slim-bookworm AS base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# uv is copied from Astral's official image (self-contained static binary).
# Pinned to a tag for reproducible builds.
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

# Dependency layer: copy the manifest files first so this layer is cached
# unless the lockfile changes, even when source code changes.
COPY pyproject.toml uv.lock ./

# Reproduce the exact locked runtime deps into /app/.venv.
# `--no-dev` skips local-only tooling (ruff/mypy/pre-commit).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Install Chromium and its OS dependencies.
RUN uv run playwright install --with-deps chromium

# Application source (copied last so code edits don't invalidate the dep layer).
COPY conftest.py ./
COPY pages ./pages
COPY tests ./tests

ENTRYPOINT ["pytest"]
CMD []
