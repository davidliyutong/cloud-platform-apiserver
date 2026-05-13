# FROM python:3.11-slim-bullseye
FROM python:3.11-bookworm
WORKDIR /opt/app
ENV PYTHONPATH "${PYTHONPATH}:/opt/app"

ARG GIT_VERSION=dev
ENV CLPL_BUILD_VERSION=${GIT_VERSION}

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

COPY src ./src

ENTRYPOINT ["uv", "run", "-m", "src", "serve"]