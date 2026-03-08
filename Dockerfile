FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

FROM base AS build

WORKDIR /build

COPY pyproject.toml README.md /build/
COPY src /build/src

RUN pip install --upgrade pip build && python -m build --wheel

FROM base AS test

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY tests /app/tests
COPY server.json /app/server.json
COPY glama.json /app/glama.json

RUN pip install --upgrade pip && pip install -e .[dev]

CMD ["pytest", "-q"]

FROM base AS runtime

ARG VERSION=0.1.1
ARG VCS_REF=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="garmin-workouts-mcp" \
      org.opencontainers.image.description="Garmin Connect workouts MCP server with strength workout support." \
      org.opencontainers.image.source="https://github.com/pranciskus/garmin-workouts-mcp" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      io.modelcontextprotocol.server.name="io.github.pranciskus/garmin-workouts-mcp"

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY --from=build /build/dist/*.whl /tmp/dist/

RUN pip install --upgrade pip && pip install /tmp/dist/*.whl && rm -rf /tmp/dist

USER appuser

ENTRYPOINT ["garmin-workouts-mcp"]
