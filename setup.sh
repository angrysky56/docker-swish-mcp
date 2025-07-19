#!/bin/bash
# Setup script for docker-swish-mcp repository

set -e

echo "Setting up docker-swish-mcp data directory..."

# Create data directories if they don't exist
mkdir -p ./swish-data/data
mkdir -p ./swish-data/config-enabled

# Fix permissions for SWISH container (runs as daemon user, uid 2, gid 2)
echo "Fixing permissions for SWISH container..."
sudo chown -R 2:2 ./swish-data
sudo chmod -R 755 ./swish-data

echo "✅ Setup complete!"
echo ""
echo "📁 Your Prolog files will be saved in: ./swish-data/data/"
echo "🌐 SWISH will be available at: http://localhost:3050"
echo ""
echo "Add the configuration from example_mcp_config.json to your Claude Desktop config.json"
