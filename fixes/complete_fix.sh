#!/bin/bash
# Complete fix and setup script for Docker SWISH MCP

set -e

echo "🚀 Docker SWISH MCP - Complete Fix & Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the docker-swish-mcp directory"
    exit 1
fi

# Step 1: Test Docker
echo -e "\n1️⃣ Testing Docker connectivity..."
if python3 fixes/test_docker.py; then
    echo "✅ Docker is ready"
else
    echo "❌ Please fix Docker issues before continuing"
    exit 1
fi

# Step 2: Clean up existing containers
echo -e "\n2️⃣ Cleaning up existing containers..."
bash fixes/cleanup_docker.sh

# Step 3: Apply fixes
echo -e "\n3️⃣ Applying MCP server fixes..."
bash fixes/apply_fixes.sh

# Step 4: Setup environment
echo -e "\n4️⃣ Setting up Python environment..."
bash setup_mcp.sh

# Step 5: Test MCP server
echo -e "\n5️⃣ Testing MCP server..."
cd "$(dirname "$0")/.."
source .venv/bin/activate
python fixes/test_mcp.py

echo -e "\n✅ Setup complete!"
echo ""
echo "📋 Final step: Update Claude Desktop configuration"
echo ""
echo "Add this to ~/.config/claude-desktop/claude_desktop_config.json:"
echo ""
cat fixes/claude_desktop_config.json | sed "s|/home/ty/Repositories/ai_workspace/docker-swish-mcp|$(pwd)|g"
echo ""
echo "Then restart Claude Desktop!"
