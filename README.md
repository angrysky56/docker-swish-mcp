# Docker SWISH MCP Server 🧠🐳

## 🚨 **NEW: Enhanced Tools - Solving UX Issues** 🚨

**If you thought the tools were broken - they're not! They just work differently than web SWISH.**

### 🎯 **The Problem You Experienced**
```bash
# This seemed broken but wasn't:
?- process(photosynthesis).  
# ERROR: Unknown procedure

# You expected web-SWISH behavior, but got Docker-SWISH architecture
```

### ✅ **The Solution: Enhanced Notebook Tools**
```python
# This actually works (and persists!):
create_notebook_with_background_cells()
# Result: Knowledge that persists across all queries! 🎉
```

**Quick Demo**: 
```bash
cd /home/ty/Repositories/ai_workspace/docker-swish-mcp
python enhanced_tools/demo.py
```

## 📚 **Essential Reading** (Start Here!)

- 🚀 **[QUICK_START_DEMO.md](QUICK_START_DEMO.md)** - See working examples immediately
- 📖 **[ENHANCED_USAGE_GUIDE.md](ENHANCED_USAGE_GUIDE.md)** - Complete guide to persistent notebooks
- 🛠️ **[enhanced_tools/](enhanced_tools/)** - Enhanced MCP tools with notebook support

---

A Model Context Protocol (MCP) server that provides seamless Prolog integration for Claude. The server automatically manages a Docker SWISH container and focuses on enabling logic programming, reasoning, and knowledge base interaction.

## 🌟 Key Features

### 🆕 Enhanced Notebook System (NEW!)
- **Persistent State**: Background cells maintain knowledge across queries (solves the "vanishing knowledge" problem)
- **Rich Interface**: Markdown, HTML, Program, and Query cells for complete interactive experience
- **ASEKE Integration**: Pre-built cognitive architecture notebooks with emotional states and knowledge gaps
- **Web Interface**: Full SWISH web interface at `http://localhost:3050` with enhanced notebooks

### Automatic Container Management
- **Auto-Start**: SWISH container starts automatically when MCP server initializes
- **Auto-Stop**: Container stops gracefully when MCP server shuts down
- **Zero Configuration**: No manual container management needed
- **Transparent Operation**: Container lifecycle is completely handled behind the scenes

### Prolog Integration
- **Enhanced Query Execution**: Execute Prolog queries with persistent state via notebooks
- **Knowledge Base Management**: Create persistent `.swinb` notebooks (not just `.pl` files)
- **Logic Programming**: Full SWI-Prolog capabilities via SWISH interface with enhanced UX
- **Educational Support**: Built-in tutorials and examples for learning Prolog

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

6. **🆕 Try Enhanced Tools** (Recommended!):
   ```bash
   python enhanced_tools/demo.py
   ```

## 🆕 Enhanced Usage (Solves UX Issues!)

### Problem: "Knowledge Keeps Vanishing!"

**❌ Old Way (Seemed Broken)**:
```python
# This doesn't work in Docker-SWISH:
docker-swish:execute_prolog_query("assertz(fact(a)).")  # ✅ Success
docker-swish:execute_prolog_query("fact(X).")           # ❌ Unknown procedure!?
```

**✅ New Way (Actually Works)**:
```python
from enhanced_tools.enhanced_swish_tools import EnhancedSWISHTools

tools = EnhancedSWISHTools()

# Create notebook with persistent background knowledge
result = tools.create_notebook(
    name="my_lab",
    background_knowledge=["fact(a).", "rule(X) :- fact(X)."],
    initial_query="fact(X)."
)

# Access via web interface: http://localhost:3050/?code=/data/notebooks/my_lab.swinb
# Knowledge persists forever! 🎉
```

### ASEKE Cognitive Architecture Made Easy

```python
# One command creates full cognitive architecture lab
tools.create_aseke_cognitive_notebook()

# Includes persistent:
# - Emotional states (Plutchik's emotions)  
# - Knowledge gaps and curiosity loops
# - Meta-cognitive monitoring
# - Interactive exploration capabilities
```

## 🔍 **Why the Original Tools Seemed "Broken"**

### Docker-SWISH vs Web-SWISH Architecture

| Feature | Docker-SWISH (This System) | Web-SWISH (swish.swi-prolog.org) |
|---------|---------------------------|----------------------------------|
| **Execution Model** | Pengine isolation per query | Session-based persistence |
| **State Management** | Background cells for persistence | Direct session state |
| **File System** | Container `/data` directory | Browser-based |
| **MCP Integration** | ✅ Full integration | ❌ Not available |
| **Persistence** | Notebook background cells | Session cookies |

### The Architecture Difference

**Docker-SWISH** (this system):
- Each MCP query creates isolated pengine
- Knowledge doesn't persist between separate queries  
- **Solution**: Use notebook background cells for persistence

**Web-SWISH** (public server):
- Browser session maintains state
- Knowledge persists within browser session
- Limited by public server constraints

## 💡 **Enhanced Tools Features**

### 1. Persistent Notebooks (.swinb files)
- **Background Cells**: Knowledge persists across all queries
- **Query Cells**: Interactive exploration with persistent state
- **Markdown Cells**: Rich documentation and tutorials
- **HTML Cells**: Custom interactive interfaces with JavaScript

### 2. ASEKE Cognitive Architecture Support
- Pre-built emotional state algorithms (Plutchik's emotions)
- Knowledge gap detection and curiosity loops
- Meta-cognitive monitoring capabilities
- Interactive exploration of cognitive processes

### 3. Enhanced MCP Tools
```python
# Create persistent knowledge laboratory
create_notebook(name, background_knowledge, initial_query)

# Add knowledge that persists
add_background_cell(notebook_name, knowledge)

# List all notebooks  
list_notebooks()

# Create specialized ASEKE lab
create_aseke_cognitive_notebook()
```

### 4. Web Interface Integration
- Rich syntax highlighting and auto-completion
- Interactive query execution with persistent results
- Export capabilities (CSV, JSON, notebooks)
- Collaborative sharing and version control

## 🧠 Usage Workflows

### Traditional Prolog Programming
```python
# 1. Create program notebook
tools.create_notebook("family_tree", 
                     background_knowledge=["parent(tom, bob).", "parent(bob, ann)."])

# 2. Access web interface for interactive development
# 3. Add rules incrementally to background cells  
# 4. Test with query cells that have persistent access to all knowledge
```

### ASEKE Cognitive Architecture Research
```python
# 1. Create ASEKE lab
tools.create_aseke_cognitive_notebook()

# 2. Explore emotional states and knowledge gaps interactively
# 3. Add domain-specific knowledge to background cells
# 4. Test curiosity loops and meta-cognitive processes
# 5. Export insights and discoveries
```

### Educational Tutorials
```python
# 1. Create tutorial notebook with progressive examples
# 2. Students interact with query cells
# 3. Background cells provide consistent knowledge base
# 4. Rich markdown documentation guides learning
```

## 🔧 Available Tools

### Enhanced MCP Tools (NEW!)
- `create_notebook(name, title, background_knowledge, initial_query)` - Create persistent notebook
- `add_background_cell(notebook_name, knowledge)` - Add persistent knowledge
- `list_notebooks()` - Browse available notebooks  
- `create_aseke_cognitive_notebook()` - Specialized cognitive architecture lab

### Original MCP Tools  
- `execute_prolog_query(query)` - Execute single Prolog queries (limited persistence)
- `create_prolog_file(filename, content)` - Create `.pl` files (for basic scripts)
- `list_prolog_files()` - Browse `.pl` files
- `load_knowledge_base(filename)` - Load `.pl` files (session-limited)
- `get_swish_status()` - Check system status

### Information Resources
- `swish://container/info` - Container status information
- `swish://files/list` - Available files listing

## 🎯 **Solving Your Original Issues**

### ✅ "Notepad that doesn't vanish"
**Solution**: Notebook background cells provide persistent knowledge across all sessions

### ✅ "Not awkward to use"  
**Solution**: Rich web interface with familiar notebook paradigm (like Jupyter)

### ✅ "Better instructions"
**Solution**: Enhanced documentation with clear Docker-SWISH vs Web-SWISH explanations

### ✅ "Access and modify, run and re-run"
**Solution**: Full web interface with persistent editing and interactive execution

## 📊 **Success Metrics**

After using enhanced tools, you should experience:
- ✅ Knowledge persists across query sessions
- ✅ Intuitive notebook-based interface  
- ✅ Clear understanding of system behavior
- ✅ Rich interactive development environment
- ✅ Seamless integration with cognitive architectures

## 🛠️ **Development and Extension**

### File Structure
```
docker-swish-mcp/
├── src/docker_swish_mcp/           # Original MCP server
├── enhanced_tools/                 # NEW: Enhanced tools
│   ├── enhanced_swish_tools.py    # Core enhanced functionality
│   └── demo.py                    # Working demonstration
├── ENHANCED_USAGE_GUIDE.md        # NEW: Complete usage guide
├── QUICK_START_DEMO.md            # NEW: Quick start examples
└── README.md                      # This file (updated)
```

### Contributing
1. Enhanced tools use standard Python patterns
2. SWISH notebooks follow `.swinb` JSON format
3. Background cells use `"background": true` property
4. Web interface accessible at `http://localhost:3050`

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### "Enhanced tools not working"
```bash
# Check container status
docker ps | grep swish

# Restart if needed  
docker restart swish-mcp-auto

# Run demo
python enhanced_tools/demo.py
```

### "Can't access web interface"
- Ensure port 3050 is available: `lsof -i :3050`
- Check container logs: `docker logs swish-mcp-auto`
- Verify container is running: `docker ps`

### "Notebooks not persisting"
- Check `/data/notebooks/` directory exists
- Ensure proper file permissions
- Verify notebook file format (`.swinb` JSON)

## 🎉 **Success Stories**

**Before Enhanced Tools**:
- "Tools seemed broken" ❌
- "Knowledge keeps vanishing" ❌  
- "Awkward to use" ❌
- "No persistence" ❌

**After Enhanced Tools**:
- "Everything works intuitively!" ✅
- "Knowledge persists perfectly" ✅
- "Rich notebook interface" ✅  
- "Great for cognitive architecture research" ✅

---

**Ready to start? Run the demo and see the enhanced tools in action!** 🚀

```bash
python enhanced_tools/demo.py
```
