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

# Which Playwright browser(s) to install at build time. Defaults to a small
# Chromium-only image; override at build time to match CI or broaden coverage:
#   docker build --build-arg PLAYWRIGHT_BROWSERS="chromium firefox webkit" .
ARG PLAYWRIGHT_BROWSERS="chromium"

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

# Create a non-root user early so later layers can set ownership correctly.
# APP_UID/APP_GID default to 1001; override at build time to match your host
# user so bind-mounted artifact dirs are writable without a permission fix-up,
# e.g. on Linux:
#   docker compose build --build-arg APP_UID=$(id -u) --build-arg APP_GID=$(id -g)
# NOTE: `--system` is intentionally omitted so a UID > 999 (SYS_UID_MAX) does
# not emit a useradd warning.
ARG APP_UID=1001
ARG APP_GID=1001
RUN groupadd --gid "${APP_GID}" appgroup \
 && useradd  --uid "${APP_UID}" --gid "${APP_GID}" \
             --home-dir /app --shell /usr/sbin/nologin --no-create-home appuser

# Dependency layer: copy the manifest files first so this layer is cached
# unless the lockfile changes, even when source code changes.
COPY pyproject.toml uv.lock ./

# Reproduce the exact locked runtime deps into /app/.venv.
# `--no-dev` skips local-only tooling (ruff/mypy/pre-commit).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Install the requested Playwright browser(s) and their OS dependencies.
# Default is Chromium only (small image); the list is configurable via the
# PLAYWRIGHT_BROWSERS build ARG above.
RUN uv run playwright install --with-deps ${PLAYWRIGHT_BROWSERS}

# Application source (copied last so code edits don't invalidate the dep layer).
# --chown so appuser owns the source tree (avoids root-owned files).
COPY --chown=appuser:appgroup conftest.py ./
COPY --chown=appuser:appgroup pages ./pages
COPY --chown=appuser:appgroup tests ./tests

# Make the runtime working dir writable by the non-root user (so pytest can
# write .pytest_cache, and bind-mounted artifact dirs created here are owned
# correctly) and ensure Playwright browsers are readable by appuser.
RUN chown appuser:appgroup /app \
 && chown -R appuser:appgroup "${PLAYWRIGHT_BROWSERS_PATH}"

USER appuser

ENTRYPOINT ["pytest"]
CMD []
