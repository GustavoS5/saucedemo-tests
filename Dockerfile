# syntax=docker/dockerfile:1
# Build:  docker build -t saucedemo-tests .
# Run:    docker run --rm -e SAUCEDEMO_PASSWORD="$SAUCEDEMO_PASSWORD" \
#           -v "$(pwd)/test-results:/app/test-results" \
#           -v "$(pwd)/allure-results:/app/allure-results" \
#           saucedemo-tests -m smoke -n auto
FROM python:3.13-slim-bookworm AS base

# Defaults to Chromium; override to build an image with additional browsers:
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

# Copy the pinned uv binary from Astral's official image.
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

# APP_UID/APP_GID default to 1001; override at build time to match your host
# user when bind-mounted artifact directories require matching ownership:
#   docker compose build --build-arg APP_UID=$(id -u) --build-arg APP_GID=$(id -g)
ARG APP_UID=1001
ARG APP_GID=1001
RUN groupadd --gid "${APP_GID}" appgroup \
 && useradd  --uid "${APP_UID}" --gid "${APP_GID}" \
             --home-dir /app --shell /usr/sbin/nologin --no-create-home appuser

# Keep dependency installation in a cacheable layer.
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN uv run playwright install --with-deps ${PLAYWRIGHT_BROWSERS}

# Copy source after dependencies to preserve the dependency cache.
COPY --chown=appuser:appgroup conftest.py ./
COPY --chown=appuser:appgroup pages ./pages
COPY --chown=appuser:appgroup tests ./tests

# pytest writes caches and artifacts under /app at runtime.
RUN chown appuser:appgroup /app \
 && chown -R appuser:appgroup "${PLAYWRIGHT_BROWSERS_PATH}"

USER appuser

ENTRYPOINT ["pytest"]
CMD []
