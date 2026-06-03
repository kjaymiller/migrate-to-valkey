FROM valkey/valkey:alpine AS valkey

FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    age \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy valkey-cli from the official image so it's available locally
COPY --from=valkey /usr/local/bin/valkey-cli /usr/local/bin/valkey-cli

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh

# Install mise and add it to PATH
RUN curl -sSfL https://mise.run | sh
ENV PATH="/root/.local/share/mise/bin:/root/.local/share/mise/shims:/root/.local/bin:$PATH"

# Install fnox globally via mise
RUN mise use -g fnox

WORKDIR /app

# Copy the entire project
COPY . /app

# Remove the wrapper script since we have the binary installed natively in the container
RUN rm -f /app/bin/valkey-cli

# Install project dependencies
RUN uv sync --frozen

# Trust the local mise config
RUN mise trust /app/mise.toml

# Ensure python virtual environment binaries are accessible
ENV PATH="/app/.venv/bin:$PATH"

# Default connection strings for local development
ENV SOURCE_CONNECTION_STRING="valkey://localhost:6379"
ENV TARGET_CONNECTION_STRING="valkey://localhost:6379"

CMD ["bash"]
