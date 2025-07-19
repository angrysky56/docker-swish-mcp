# Docker SWISH MCP Server
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY example_mcp_config.json ./

# Create data directory
RUN mkdir -p /app/swish-data

# Expose MCP port (if needed for HTTP transport)
EXPOSE 3050

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import docker_swish_mcp; print('healthy')" || exit 1

# Run the MCP server
CMD ["python", "-m", "docker_swish_mcp.main"]
