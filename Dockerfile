# Use the official uv image for build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set environment variables for faster/cleaner uv builds
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=60

WORKDIR /app

# Mount cache directory for uv and copy config files to install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy source code files
COPY config.py data.py services.py security.py server.py ./

# Sync the project (installs dependencies in the virtualenv)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Final production stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy virtual environment and source code from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/config.py /app/data.py /app/services.py /app/security.py /app/server.py /app/

# Place the virtual environment's bin directory on the PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Start Uvicorn pointing to server:app on host 0.0.0.0 and port 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
