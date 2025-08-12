FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build-image

WORKDIR /usr/src/app
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev


# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /usr/src/app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.13-slim
WORKDIR /usr/src/app
COPY --from=build-image /usr/src/app /usr/src/app/
CMD ["./.venv/bin/python", "-m", "scrapy", "crawl", "sheriffwebsites"]
