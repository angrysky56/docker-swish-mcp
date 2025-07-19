#!/bin/bash
# Cleanup script for Docker SWISH containers

echo "🧹 Docker SWISH Cleanup Script"
echo "=" * 60

# Find all SWISH containers
echo -e "\n📋 Looking for SWISH containers..."
CONTAINERS=$(docker ps -a --filter "ancestor=swipl/swish" --format "{{.ID}} {{.Names}} {{.Status}}")

if [ -z "$CONTAINERS" ]; then
    echo "✅ No SWISH containers found"
else
    echo "Found SWISH containers:"
    echo "$CONTAINERS"
    
    echo -e "\n🛑 Stopping and removing SWISH containers..."
    docker ps -a --filter "ancestor=swipl/swish" -q | xargs -r docker stop
    docker ps -a --filter "ancestor=swipl/swish" -q | xargs -r docker rm
    echo "✅ Containers cleaned up"
fi

# Check for containers using port 3050
echo -e "\n🔍 Checking port 3050..."
PORT_CONTAINERS=$(docker ps --filter "publish=3050" --format "{{.ID}} {{.Names}}")

if [ -z "$PORT_CONTAINERS" ]; then
    echo "✅ Port 3050 is free"
else
    echo "⚠️ Containers using port 3050:"
    echo "$PORT_CONTAINERS"
    
    read -p "Stop these containers? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker ps --filter "publish=3050" -q | xargs -r docker stop
        docker ps --filter "publish=3050" -q | xargs -r docker rm
        echo "✅ Port 3050 freed"
    fi
fi

# Check for dangling volumes
echo -e "\n📦 Checking for dangling volumes..."
VOLUMES=$(docker volume ls -f dangling=true -q | wc -l)
if [ "$VOLUMES" -gt 0 ]; then
    echo "Found $VOLUMES dangling volumes"
    read -p "Remove dangling volumes? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        echo "✅ Volumes cleaned"
    fi
fi

echo -e "\n✅ Cleanup complete!"
echo "You can now start fresh with the MCP server"