# Stage 1: Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/

# Install dependencies and project (non-editable)
RUN uv sync --frozen --no-dev --no-editable


# Stage 2: Runtime stage
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Put the venv's Python on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run as non-root user (security)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
