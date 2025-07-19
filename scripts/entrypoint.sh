#!/bin/bash
# Entrypoint script to handle Docker permissions automatically

set -e

# Get host user information
HOST_UID=${HOST_UID:-$(id -u)}
HOST_GID=${HOST_GID:-$(id -g)}

# Create data directory with proper permissions
mkdir -p /app/swish-data/data
mkdir -p /app/swish-data/config-enabled

# If running as root, create a user matching host permissions
if [ "$(id -u)" = "0" ]; then
    # Create group if it doesn't exist
    if ! getent group hostgroup > /dev/null 2>&1; then
        groupadd -g "${HOST_GID}" hostgroup
    fi
    
    # Create user if it doesn't exist  
    if ! getent passwd hostuser > /dev/null 2>&1; then
        useradd -u "${HOST_UID}" -g "${HOST_GID}" -d /app -s /bin/bash hostuser
    fi
    
    # Change ownership of data directory
    chown -R "${HOST_UID}:${HOST_GID}" /app/swish-data
    
    # Switch to host user for main process
    exec gosu hostuser "$@"
else
    # Already running as non-root, just ensure data directory permissions
    chmod -R 755 /app/swish-data
fi

# Execute the main command
exec "$@"
