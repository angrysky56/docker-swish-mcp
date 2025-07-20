# Docker SWISH MCP Server 🧠🐳

A Model Context Protocol (MCP) server that provides seamless Prolog integration for Claude. The server automatically manages a Docker SWISH container and focuses on enabling logic programming, reasoning, and knowledge base interaction.

## 🌟 Key Features

### Automatic Container Management
- **Auto-Start**: SWISH container starts automatically when MCP server initializes
- **Auto-Stop**: Container stops gracefully when MCP server shuts down
- **Zero Configuration**: No manual container management needed
- **Transparent Operation**: Container lifecycle is completely handled behind the scenes

### Prolog Integration
- **Direct Query Execution**: Execute Prolog queries directly from Claude
- **Knowledge Base Management**: Create, load, and manage `.pl` files
- **Logic Programming**: Full SWI-Prolog capabilities via SWISH interface
- **Educational Support**: Built-in prompts for learning Prolog

### AI-Assisted Logic Programming
- **Programming Assistance**: Context-aware Prolog programming help
- **Rule Creation**: Guided creation of domain-specific logic rules
- **Best Practices**: Automated suggestions following Prolog conventions
- **Debugging Support**: Systematic debugging techniques and patterns

## 🚀 Quick Start

### Prerequisites
- Docker installed and running
- Python 3.10+
- `uv` package manager

### Installation

1. **Navigate to the project**:
   ```bash
   cd /home/ty/Repositories/ai_workspace/docker-swish-mcp
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

4. **Add to Claude Desktop Configuration**:
   Copy the contents of `example_mcp_config.json` to your Claude Desktop config:
   ```bash
   # Linux/Mac
   nano ~/.config/claude-desktop/claude_desktop_config.json
   ```

5. **Restart Claude Desktop** - The SWISH container will start automatically!

## 🧠 Usage

Once configured, you can immediately start using Prolog with Claude:

### Basic Prolog Queries
```
Claude: Execute this Prolog query: member(X, [1,2,3,4,5]).
```

### Create Knowledge Bases
```
Claude: Create a family relationships knowledge base with facts about parents and rules for grandparents.
```

### Logic Programming
```
Claude: Help me write Prolog rules to solve the Tower of Hanoi puzzle.
```

### Load and Test Knowledge
```
Claude: Load the family knowledge base and test some relationship queries.
```

## 🔧 Available Tools

### Primary Prolog Tools
- `execute_prolog_query(query)` - Execute Prolog queries directly
- `create_prolog_file(filename, content)` - Create Prolog knowledge bases
- `list_prolog_files()` - Browse available `.pl` files
- `load_knowledge_base(filename)` - Consult/load Prolog files
- `get_swish_status()` - Check Prolog environment status

### AI Assistance Prompts
- `prolog_programming_assistant()` - Tailored Prolog programming help
- `logic_rule_creation()` - Domain-specific rule design guidance

### Information Resources
- `swish://container/info` - Container status information
- `swish://files/list` - Available Prolog files listing

## 💡 Example Workflows

### 1. Logic Programming Tutorial
```prolog
% Claude can help create this knowledge base
% Facts about family relationships
parent(tom, bob).
parent(bob, ann).
parent(bob, pat).
parent(ann, jim).

% Rules for family relationships
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
ancestor(X, Z) :- parent(X, Z).
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).

% Query examples:
% ?- grandparent(tom, ann).
% ?- ancestor(tom, jim).
% ?- findall(X, ancestor(tom, X), Descendants).
```

### 2. Problem Solving with Logic
```prolog
% Example: Solving logic puzzles
% Houses puzzle with colors, pets, and nationalities

house(red, british, dog).
house(green, irish, cat).
house(blue, german, fish).

next_to(house(red,_,_), house(blue,_,_)).
lives_with(Person, Pet) :- house(_, Person, Pet).

% Query: Who lives with what pet?
% ?- lives_with(Person, Pet).
```

### 3. Deterministic Agent Rules
```prolog
% Agent capability rules (inspired by the Prolog agent guide)
can_execute(shell_command).
can_execute(file_io).
can_write(python).

% Task authorization logic
can_perform_task(create_file(Name, Content)) :-
    can_execute(file_io),
    is_valid_filename(Name),
    is_safe_content(Content).

is_valid_filename(Name) :- 
    atom_string(Name, NameStr),
    \+ sub_string(NameStr, _, _, _, '..').

is_safe_content(Content) :-
    atom_string(Content, ContentStr),
    \+ sub_string(ContentStr, _, _, _, 'rm -rf').
```

## 🏗️ Architecture

### Automatic Container Management
- **Lifecycle Integration**: Container starts/stops with MCP server lifecycle
- **Health Monitoring**: Automatic readiness checking and health verification
- **Data Persistence**: Volume mounting for persistent knowledge bases
- **Error Recovery**: Graceful handling of Docker issues and container failures

### Prolog Environment
- **SWI-Prolog**: Full SWI-Prolog implementation via SWISH
- **Web Interface**: Browser-accessible at `http://localhost:3050` (when running)
- **Knowledge Persistence**: `.pl` files stored in `./swish-data/data/`
- **Safe Execution**: Anonymous mode for secure query execution

### MCP Integration
- **FastMCP Framework**: Built on the modern FastMCP framework
- **Async Operations**: Non-blocking query execution and file operations
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Logging**: Proper stderr logging for MCP compatibility

## 🔒 Security & Safety

### Container Security
- **Anonymous Mode**: SWISH runs in anonymous mode (sandboxed queries)
- **Volume Isolation**: Data directory properly isolated
- **Network Isolation**: Container only exposes necessary ports
- **Resource Limits**: Automatic resource management and cleanup

### Query Safety
- **Input Validation**: Prolog query sanitization and validation
- **Timeout Controls**: Configurable timeouts for query execution
- **Error Isolation**: Query errors don't affect container stability

## 📖 Configuration

### Example MCP Configuration
```json
{
  "mcpServers": {
    "docker-swish": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/ty/Repositories/ai_workspace/docker-swish-mcp",
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

### Customization Options
- **Port Configuration**: Default port 3050 (configurable)
- **Data Directory**: `./swish-data/` (persistent across restarts)
- **Container Name**: `swish-mcp-auto` (auto-managed)
- **Timeout Settings**: Configurable query timeouts

## 🛠️ Development

### Project Structure
```
docker-swish-mcp/
├── src/docker_swish_mcp/
│   ├── __init__.py
│   ├── main.py              # Main MCP server implementation
│   └── __about__.py         # Version info
├── pyproject.toml           # Package configuration
├── example_mcp_config.json  # Claude Desktop config
├── README.md               # This file
└── swish-data/             # Data directory (auto-created)
    └── data/               # Prolog files location
```

### Contributing
1. Follow MCP development best practices
2. Use `uv` for dependency management
3. Add type hints and comprehensive docstrings
4. Test with real Prolog use cases
5. Ensure stderr logging for MCP compatibility

### Testing
```bash
# Test the server
uv run python -m docker_swish_mcp.main

# Test with MCP Inspector
mcp dev src/docker_swish_mcp/main.py
```

## 🔗 Related Resources

- [SWI-Prolog Documentation](https://www.swi-prolog.org/pldoc/doc_for?object=manual)
- [SWISH Tutorial](https://swish.swi-prolog.org/example/tutorial.swinb)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Logic Programming Guide](https://www.learnprolognow.org/)

## ✨ What Makes This Different

### Traditional Approach Problems:
- Manual container start/stop commands
- Complex setup and configuration
- Container management mixed with logic programming
- Unclear separation of concerns

### This Solution:
- **Zero Manual Container Management**: Everything automatic
- **Prolog-Focused**: Tools designed for logic programming tasks
- **Seamless Integration**: Container lifecycle handled transparently
- **Educational Support**: Built-in learning assistance for Prolog

### Perfect For:
- **Logic Programming**: Rules, facts, reasoning, constraint solving
- **Educational Use**: Learning Prolog with AI assistance
- **Knowledge Bases**: Structured information and inference
- **Deterministic Agents**: Rule-based decision systems (as described in the Prolog agent guide)

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Docker not available**:
   - Ensure Docker Desktop is running
   - Check Docker permissions: `docker ps`
   - Verify user is in docker group (Linux)

2. **Container won't start**:
   - Check port 3050 is available: `lsof -i :3050`
   - Ensure sufficient disk space
   - Check Docker logs: `docker logs swish-mcp-auto`

3. **Prolog queries timeout**:
   - Check SWISH container is responsive
   - Use `get_swish_status()` to verify readiness
   - Restart MCP server if needed

4. **Permission errors**:
   - Ensure data directory is writable
   - Check Docker volume permissions
   - Verify file ownership in `./swish-data/`

### Debug Commands
```bash
# Check container status
docker ps | grep swish

# View container logs
docker logs swish-mcp-auto

# Test SWISH directly
curl http://localhost:3050/

# Check MCP server logs
# (logs appear in Claude Desktop or terminal when running directly)
```

## 🎯 Success Stories

This MCP server enables:
- **Rapid Prototyping**: Quick logic rule development and testing
- **Educational Support**: Learning Prolog with AI guidance
- **Knowledge Engineering**: Building and testing knowledge bases
- **Deterministic AI**: Creating rule-based, predictable agent behavior

---

**Ready to start logic programming with Claude? Install and begin reasoning!** 🧠✨
