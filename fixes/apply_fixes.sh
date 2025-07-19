#!/bin/bash
# Apply fixes to Docker SWISH MCP Server

set -e

echo "🔧 Applying Docker SWISH MCP fixes..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the docker-swish-mcp directory"
    exit 1
fi

# Backup original main.py if it exists
if [ -f "src/docker_swish_mcp/main.py" ] && [ ! -f "src/docker_swish_mcp/main.backup.py" ]; then
    echo "📦 Backing up original main.py..."
    cp src/docker_swish_mcp/main.py src/docker_swish_mcp/main.backup.py
fi

# Copy improved main.py
echo "📝 Installing improved main.py..."
cp fixes/improved_main.py src/docker_swish_mcp/main.py

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x setup_mcp.sh
chmod +x fixes/test_mcp.py

# Show the correct configuration
echo ""
echo "✅ Fixes applied successfully!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Run the setup script:"
echo "   ./setup_mcp.sh"
echo ""
echo "2. Update your Claude Desktop configuration with:"
echo ""
cat fixes/claude_desktop_config.json | sed "s|/home/ty/Repositories/ai_workspace/docker-swish-mcp|$(pwd)|g"
echo ""
echo "3. Restart Claude Desktop"
echo ""
echo "4. Test with: python fixes/test_mcp.py"
echo ""
echo "📚 See fixes/FIX_SUMMARY.md for detailed information"
