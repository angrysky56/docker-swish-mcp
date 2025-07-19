#!/bin/bash
# Setup script for Docker SWISH MCP Server

set -e  # Exit on error

echo "🚀 Setting up Docker SWISH MCP Server..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the docker-swish-mcp directory"
    exit 1
fi

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create and activate virtual environment
echo "📦 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    uv venv --python 3.12 --seed
fi

# Install the package in development mode
echo "📚 Installing dependencies..."
uv pip install -e .

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p swish-data/data
chmod 755 swish-data swish-data/data

# Create Claude Desktop config directory if it doesn't exist
CONFIG_DIR="$HOME/.config/claude-desktop"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "📁 Creating Claude Desktop config directory..."
    mkdir -p "$CONFIG_DIR"
fi

# Show the correct configuration
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Add this to your Claude Desktop configuration:"
echo "   $CONFIG_DIR/claude_desktop_config.json"
echo ""
cat << 'EOF'
{
  "mcpServers": {
    "docker-swish": {
      "command": "uv",
      "args": [
        "--directory",
        "$(pwd)",
        "run",
        "python",
        "-m",
        "docker_swish_mcp.main"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF

echo ""
echo "💡 Replace \$(pwd) with the absolute path: $(pwd)"
echo ""
echo "🔄 After updating the config, restart Claude Desktop"
echo ""
echo "📝 Example usage in Claude:"
echo "   - 'Start a SWISH container for Prolog programming'"
echo "   - 'Create a family relationships knowledge base'"
echo "   - 'Execute Prolog query: member(X, [1,2,3,4,5]).'"
