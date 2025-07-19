# Docker SWISH MCP - Fixed for Seamless User Setup
FROM python:3.12-slim

# Install system dependencies including Docker CLI
RUN apt-get update && apt-get install -y \
    docker.io \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create app user with sudo privileges for Docker access
RUN useradd -m -s /bin/bash app && \
    usermod -aG docker app && \
    echo 'app ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/

# Create a script to handle permissions automatically
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO

# Use entrypoint to handle permissions
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "docker_swish_mcp.main"]
