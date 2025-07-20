# 🚀 Quick Start Demo - Enhanced SWISH Tools

## The Problem You Experienced

```bash
# You tried this and it seemed broken:
$ docker-swish:execute_prolog_query("process(photosynthesis).")
# ERROR: Unknown procedure: process/1 - "WTF?!"
```

## The Solution (Actually Works!)

### Step 1: Create Persistent Notebook
```python
from enhanced_tools.enhanced_swish_tools import EnhancedSWISHTools

tools = EnhancedSWISHTools()

# Create notebook with persistent background knowledge
result = tools.create_notebook(
    name="demo_lab",
    title="Demo: Persistent Knowledge That Actually Works!",
    background_knowledge=[
        "process(photosynthesis).",
        "location(photosynthesis, chloroplast).", 
        "emotion(curiosity, high).",
        "test_rule(X) :- process(X)."
    ],
    initial_query="process(X)."
)

print(result["usage_instructions"])
```

### Step 2: Access Web Interface 
```bash
# Open this URL in your browser:
http://localhost:3050/?code=/data/notebooks/demo_lab.swinb

# You'll see:
# 🔒 Background cells (persistent knowledge)
# ▶️ Query cells (interactive testing)
# 📝 Markdown cells (documentation)
```

### Step 3: Test Persistent Knowledge
```prolog
% In the web interface, try these queries:
?- process(X).           % ✅ X = photosynthesis
?- emotion(E, L).        % ✅ E = curiosity, L = high  
?- test_rule(X).         % ✅ X = photosynthesis
?- location(P, L).       % ✅ P = photosynthesis, L = chloroplast
```

**SUCCESS!** 🎉 Knowledge persists across all queries!

## ASEKE Cognitive Architecture Demo

### Create Full ASEKE Lab
```python
# One command creates complete cognitive architecture notebook
aseke_result = tools.create_aseke_cognitive_notebook()

print(f"ASEKE Lab URL: {aseke_result['web_url']}")
```

### Interactive ASEKE Exploration
```prolog
% Test emotional states
?- emotional_state(State, Level).

% Detect knowledge gaps  
?- detect_knowledge_gap(Domain, Gap).

% Explore curiosity loop
?- generate_inquiry(calvin_cycle, key_enzyme, Query).

% Meta-cognitive monitoring
?- meta_state(State).
```

## Key Insight: Background Cells = Persistent State

### ❌ Old Way (Doesn't Work in Docker-SWISH)
```
1. Create .pl file
2. Try to consult() in separate query
3. Knowledge vanishes between queries
4. Frustration!
```

### ✅ New Way (Works Perfectly)  
```
1. Create .swinb notebook
2. Put knowledge in background cells (🔒)
3. Use query cells for interaction (▶️)
4. Knowledge persists forever!
```

## File Structure Created
```
/data/notebooks/
├── demo_lab.swinb                    # Basic demo notebook
├── aseke_cognitive_architecture.swinb # Full ASEKE lab
└── [your_custom_notebooks.swinb]     # Your experiments

# Each notebook contains:
# - Persistent background cells (🔒)
# - Interactive query cells (▶️)  
# - Documentation (📝)
# - Rich HTML interfaces (🌐)
```

## Browser Experience
1. **Rich Editor**: Syntax highlighting, auto-completion
2. **Persistent State**: Background cells maintain knowledge
3. **Interactive Queries**: Run/re-run queries anytime
4. **Export Results**: CSV, JSON, visualization
5. **Collaborative**: Share notebooks with team

## Why This Works Better

**Docker-SWISH Architecture**:
- Containerized execution ✅
- File system persistence ✅  
- MCP integration ✅
- Background cell state management ✅

**Web SWISH Architecture**: 
- Browser-based execution ✅
- Session-based state ⚠️
- Public server limitations ⚠️
- No local file integration ❌

## Next Steps

1. **Run this demo** to see persistent state working
2. **Explore web interface** for rich editing experience  
3. **Create domain-specific notebooks** for your projects
4. **Build knowledge incrementally** with background cells

The "broken" tools are actually **more powerful** than web SWISH - they just work differently! 🎯

---

**Run this demo now**: 
```bash
cd /home/ty/Repositories/ai_workspace/docker-swish-mcp
python enhanced_tools/demo.py
```
