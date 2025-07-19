# Docker SWISH MCP Server 🐳🧠

A Model Context Protocol (MCP) server for managing Docker SWISH containers and interacting with SWI-Prolog knowledge bases. This server bridges the gap between AI assistants and logic programming, enabling deterministic reasoning and knowledge base management.

## 🌟 Features

### Container Management
- **Start/Stop SWISH**: Launch Docker containers with configurable settings
- **Status Monitoring**: Real-time container health and service status
- **Configuration Management**: Set up authentication, HTTPS, and port mapping
- **Log Access**: View container logs and debugging information

### Prolog Integration
- **Query Execution**: Execute Prolog queries directly against SWISH
- **Knowledge Base Management**: Create, edit, and organize .pl files
- **File Operations**: List, read, and manage Prolog knowledge bases
- **Real-time Interaction**: Interactive Prolog programming environment

### AI-Assisted Development
- **Programming Prompts**: Tailored assistance for Prolog development
- **Logic Rule Creation**: Guided creation of domain-specific rules
- **Debugging Support**: Systematic debugging prompts and techniques
- **Knowledge Base Design**: Structured approach to KB architecture

## 🚀 Quick Start

### Prerequisites
- Docker installed and running
- Python 3.10+
- `uv` package manager


### Step 1: Add to Claude Desktop Configuration

Add this to your Claude Desktop `config.json` file:

```json
{
  "mcpServers": {
    "docker-swish": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "./swish-data:/data",
        "-p",
        "3050:3050",
        "swipl/swish"
      ]
    }
  }
}
```
# Permission issues

If you encounter permission issues, ensure you have the correct permissions for the `/tmp/swish-data` directory.

run
```bash
./setup.sh
```
### Step 2: That's It!

The container automatically:
- ✅ Handles permissions properly using `/tmp/swish-data`
- ✅ Creates necessary directories
- ✅ Runs SWISH on `http://localhost:3050`
- ✅ Provides Prolog file management tools
- ✅ Works for any user without manual setup

## Example Usage

```plaintext
Claude: Let me create a knowledge base about photosynthesis and test some Prolog queries.

# Creates photosynthesis.pl with facts and rules
# Executes queries like: ?- what_do_we_know_about(photosynthesis, Facts).
# Shows results in an organized format
```

## Available Tools

Once configured, you get these MCP tools in Claude:

- `start_swish_container()` - Start SWISH with custom options
- `stop_swish_container()` - Stop the running container
- `get_swish_status()` - Check container and service status
- `execute_prolog_query(query)` - Run Prolog queries directly
- `create_prolog_file(filename, content)` - Create `.pl` files
- `list_prolog_files()` - Show all Prolog knowledge bases
- `configure_swish_auth(mode)` - Set authentication options

### Installation

1. **Clone or navigate to the project**:
   ```bash
   cd /docker-swish-mcp
   ```

2. **Set up Python environment**:
   ```bash
   uv venv --python 3.12 --seed
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   uv add -e .
   ```

4. **Configure Claude Desktop**:
   Add the contents of `example_mcp_config.json` to your Claude Desktop configuration:
   ```bash
   # Linux/Mac
   nano ~/.config/claude-desktop/claude_desktop_config.json

   # Or copy the example
   cp example_mcp_config.json ~/.config/claude-desktop/
   ```

5. **Restart Claude Desktop** to load the MCP server

## 🔧 Usage

### Container Management

**Start SWISH Container**:
```
Start a SWISH container on port 3050 with anonymous authentication
```

**Configure Authentication**:
```
Set up SWISH with 'social' authentication for Google/StackOverflow login
```

**Check Status**:
```
Get current container status and SWISH accessibility
```

### Prolog Programming

**Execute Queries**:
```
Run Prolog query: member(X, [1,2,3,4,5]).
```

**Create Knowledge Base**:
```
Create a family relationships knowledge base with facts and rules
```

**Debug Code**:
```
Help debug this Prolog predicate that's not working correctly
```

### Knowledge Base Management

**List Files**:
```
Show all Prolog files in the knowledge base
```

**View Content**:
```
Show the content of family_relations.pl
```

**Get Summary**:
```
Provide an overview of the current knowledge base
```

## 🛠️ Available Tools

### Container Tools
- `start_swish_container()` - Launch SWISH with custom configuration
- `stop_swish_container()` - Stop and remove container
- `get_swish_status()` - Container and service status
- `configure_swish_auth()` - Authentication setup

### Prolog Tools
- `execute_prolog_query()` - Run queries against SWISH
- `create_prolog_file()` - Create new .pl knowledge files
- `list_prolog_files()` - Browse available files

### Resources
- `swish://container/logs` - Container logs
- `swish://files/{filename}` - Prolog file content
- `swish://knowledge-base` - KB summary

### AI Prompts
- `prolog_programming_assistant()` - Tailored programming help
- `logic_rule_creation()` - Domain-specific rule design
- `debug_prolog_code()` - Systematic debugging assistance
- `knowledge_base_design()` - Architecture guidance

## 🏗️ Architecture

### Docker SWISH Integration
The server manages Docker containers running the official `swipl/swish` image, which provides:
- Web-based SWI-Prolog environment
- Interactive query interface
- File management and persistence
- Authentication and security options

### MCP Protocol
Built on FastMCP framework with:
- Async/await patterns for Docker operations
- Proper error handling and logging
- Resource cleanup and signal handling
- Type hints and comprehensive documentation

### Data Management
- **Data Directory**: `./swish-data/` (configurable)
- **Prolog Files**: Stored in `data/` subdirectory
- **Configuration**: Managed in `config-enabled/`
- **Persistence**: Docker volumes for data retention

## 🔒 Security Considerations

### Authentication Modes
- **Anonymous** (default): Sandboxed queries only
- **Social**: Google/StackOverflow login
- **Always**: Full authentication required

### Container Security
- Non-root user execution when possible
- Data directory permissions management
- Network isolation options
- HTTPS support with self-signed certificates

### Input Validation
- Prolog query sanitization
- File path validation
- Docker parameter filtering
- Error message sanitization

## 🧪 Example Workflows

### 1. Logic Programming Tutorial
```bash
# Start container
start_swish_container(port=3050, auth_mode="anon")

# Create learning materials
create_prolog_file("tutorial", "
% Basic facts
likes(mary, food).
likes(mary, wine).
likes(john, wine).

% Rules
happy(X) :- likes(X, wine).
")

# Test queries
execute_prolog_query("happy(X).")
```

### 2. Knowledge Base Development
```bash
# Design domain model
knowledge_base_design("Family relationships and genealogy",
                     "Query ancestors, descendants, relationships")

# Create structured KB
create_prolog_file("family", "
% Facts
parent(tom, bob).
parent(bob, ann).
parent(bob, pat).

% Rules
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
ancestor(X, Z) :- parent(X, Z).
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).
")

# Test reasoning
execute_prolog_query("ancestor(tom, ann).")
```

### 3. Deterministic Agent Logic
```bash
# Create agent rules (from Prolog agent documentation)
create_prolog_file("agent_rules", "
% Agent capabilities
can_execute(shell_command).
can_execute(file_io).
can_write(python).

% Task authorization rules
can_perform_task(create_file(Name, Content)) :-
    can_execute(file_io),
    is_valid_filename(Name),
    is_safe_content(Content).
")

# Test agent logic
execute_prolog_query("can_perform_task(create_file('app.py', 'print(hello)')).")
```

## 📝 Development

### Project Structure
```
docker-swish-mcp/
├── src/docker_swish_mcp/
│   ├── __init__.py          # Package initialization
│   └── main.py              # MCP server implementation
├── pyproject.toml           # Package configuration
├── example_mcp_config.json  # Claude Desktop config
└── README.md               # This file
```

### Contributing
1. Follow MCP development guidelines
2. Use `uv` for dependency management
3. Add type hints and docstrings
4. Test with real SWISH containers
5. Log to stderr for MCP compatibility

### Testing
```bash
# Start development server
uv run python -m docker_swish_mcp.main

# Test with MCP Inspector
mcp dev src/docker_swish_mcp/main.py
```

## 🔗 Related Projects

- [Docker SWISH](https://github.com/SWI-Prolog/docker-swish) - Base Docker image
- [SWI-Prolog](https://www.swi-prolog.org/) - Prolog implementation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python MCP framework

## 📄 License

MIT License - see LICENSE file for details.

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

For more help, check container logs with `get_swish_status()` or examine Docker logs directly.
