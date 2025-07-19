# Docker SWISH MCP Server - User-Friendly Setup

A Model Context Protocol (MCP) server for managing Docker SWISH (SWI-Prolog for SHaring) containers with **zero manual permission configuration**.

## Quick Setup for Claude Desktop

### Step 1: Add to Claude Desktop Configuration

Add this to your Claude Desktop `config.json` file:

```json
{
  "mcpServers": {
    "docker-swish": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--name", "swish-mcp",
        "-p", "3050:3050",
        "-v", "/tmp/swish-data:/data",
        "swipl/swish"
      ]
    }
  }
}
```

### Step 2: That's It!

The container automatically:
- ✅ Handles permissions properly using `/tmp/swish-data`
- ✅ Creates necessary directories
- ✅ Runs SWISH on `http://localhost:3050`
- ✅ Provides Prolog file management tools
- ✅ Works for any user without manual setup

## Available Tools

Once configured, you get these MCP tools in Claude:

- `start_swish_container()` - Start SWISH with custom options
- `stop_swish_container()` - Stop the running container
- `get_swish_status()` - Check container and service status
- `execute_prolog_query(query)` - Run Prolog queries directly
- `create_prolog_file(filename, content)` - Create `.pl` files
- `list_prolog_files()` - Show all Prolog knowledge bases
- `configure_swish_auth(mode)` - Set authentication options

## Example Usage

```plaintext
Claude: Let me create a knowledge base about photosynthesis and test some Prolog queries.

# Creates photosynthesis.pl with facts and rules
# Executes queries like: ?- what_do_we_know_about(photosynthesis, Facts).
# Shows results in an organized format
```

## Advanced Configuration (Optional)

### Alternative: Development Mode
For development with the full MCP server features:

```json
{
  "mcpServers": {
    "docker-swish-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/docker-swish-mcp",
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
```

### Authentication Options
- `anon` - Anonymous access (default, sandboxed)
- `social` - Social login (Google, StackOverflow)
- `always` - Full authentication required

## Troubleshooting

### Container Issues
- **Port conflict**: Change `-p 3050:3050` to `-p 3051:3050`
- **Permission denied**: The setup uses `/tmp/swish-data` to avoid permission issues
- **Container exists**: Stop with `docker stop swish-mcp` or use `--rm` flag

### Data Persistence
- Files stored in `/tmp/swish-data` (temporary by design)
- For permanent storage, change volume to `$HOME/swish-data:/data`
- The container handles permissions automatically

## Why This Works

**Traditional Problem**: Docker volume permissions require manual `chown` commands

**This Solution**:
- Uses `/tmp` directory (world-writable by default)
- SWISH container creates proper directory structure
- No manual permission fixes needed
- Works across different host systems

## Development

To build and test locally:

```bash
# Build the image
docker build -t docker-swish-mcp .

# Test the configuration
# Use the config above in Claude Desktop
```

## License

MIT License - See LICENSE file for details.

---

**Created for seamless integration with Claude Desktop and MCP ecosystem.**
