# Use official Python image
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy all required files
COPY pyproject.toml uv.lock README.md ./

# Copy source code
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Set environment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Use shell form to expand PORT
CMD uv run uvicorn kenpom_mcp.http_server:app --host 0.0.0.0 --port $PORT
