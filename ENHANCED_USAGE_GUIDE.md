# Enhanced SWISH-Prolog MCP Server - User Guide

## 🚀 Quick Start (The Non-Broken Way!)

**TL;DR**: Use notebooks with background cells for persistent knowledge. The tools work perfectly - they just work differently than web SWISH!

## 🔍 What You Experienced (And Why)

### "It Seemed Broken But Wasn't" 

```python
# ❌ This LOOKED like it should work but didn't
docker-swish:execute_prolog_query("process(photosynthesis).")
# Result: Unknown procedure - WTF?!

# ✅ This ACTUALLY works (Docker-SWISH vs Web-SWISH difference)  
docker-swish:create_notebook_with_background_cells(...)
# Result: Persistent knowledge that actually stays!
```

**The Issue**: Docker-SWISH uses pengine isolation - each query is a separate session. It's not broken, it's different!

**The Solution**: Use SWISH notebooks with background cells for persistent state.

## 🎯 Core Problem Solved: Persistent Notepad

### Before (Frustrating):
```
Query 1: assertz(fact(a)).        # ✅ Works
Query 2: fact(X).                 # ❌ "Unknown procedure" - knowledge vanished!
```

### After (Actually Useful):
```
Background Cell: fact(a).         # ✅ Persists forever
Query Cell: fact(X).              # ✅ X = a (knowledge stays!)
```

## 📋 Enhanced Tool Usage

### 1. Create Persistent Notebooks (Not Files!)

```python
# ✅ Do This: Create notebook with persistent background
result = enhanced_tools.create_notebook(
    name="my_knowledge_base",
    title="My Persistent Knowledge Lab", 
    background_knowledge=[
        "process(photosynthesis).",
        "location(photosynthesis, chloroplast).",
        "emotion(curiosity, high)."
    ],
    initial_query="process(X)."
)

# Result: Notebook with persistent state that actually works!
print(result["web_url"])  # Access via browser for rich interface
```

### 2. Add Knowledge That Persists

```python
# ✅ Add to existing notebook (knowledge persists)
enhanced_tools.add_background_cell(
    "my_knowledge_base",
    "new_fact(important_insight)."
)

# Now this knowledge is permanently available in the notebook!
```

### 3. Interactive Exploration (Web Interface)

**Access**: `http://localhost:3050/?code=/data/notebooks/my_knowledge_base.swinb`

- **Background cells** (🔒): Persistent knowledge
- **Query cells** (▶️): Interactive testing  
- **Markdown cells** (📝): Documentation
- **HTML cells** (🌐): Custom interfaces

## 🧠 ASEKE Cognitive Architecture Made Easy

### Pre-Built ASEKE Notebook

```python
# Creates full ASEKE cognitive architecture notebook
result = enhanced_tools.create_aseke_cognitive_notebook()

# Includes persistent:
# - Emotional states (Plutchik's emotions)
# - Knowledge gaps and curiosity loops
# - Meta-cognitive monitoring
# - Photosynthesis domain example

print(f"ASEKE Lab: {result['web_url']}")
```

### Interactive ASEKE Exploration

**Background Cells** (Persistent):
```prolog
% Emotional State Algorithms
emotion(curiosity, high).
emotional_state(engagement, growing).

% Knowledge Substrate  
process(photosynthesis).
knowledge_gap(calvin_cycle, key_enzyme).

% Curiosity Loop
detect_knowledge_gap(Domain, Gap) :- 
    knowledge_gap(Domain, Gap),
    \+ has_knowledge(Domain, Gap).
```

**Query Cells** (Interactive):
```prolog
?- emotion(State, Level).
?- detect_knowledge_gap(calvin_cycle, Gap).
?- emotional_state(Context, Level).
```

## 🔧 Workflow Comparison

### Old Workflow (Seemed Broken):
1. Create .pl file ❌
2. Load with consult() ❌  
3. Query separately ❌
4. Knowledge vanishes ❌
5. Frustration! 😤

### New Workflow (Actually Works):
1. Create .swinb notebook ✅
2. Add background cells ✅
3. Use web interface ✅  
4. Knowledge persists ✅
5. Success! 🎉

## 🌐 Web Interface Features

### Background Cell Management
- **Mark as Background**: Click 🔒 button to make cell persistent
- **Edit Background**: Modify persistent knowledge anytime
- **Add Background**: + button → Program cell → Mark as background

### Query Execution
- **Run Query**: Click ▶️ to execute against background knowledge
- **View Results**: Rich formatting with tables, graphs, etc.
- **Export Results**: Download as CSV, JSON, etc.

### Documentation
- **Markdown Cells**: Rich text with LaTeX, links, images
- **HTML Cells**: Custom interfaces with JavaScript
- **Export Notebook**: Share complete interactive documents

## 🛠️ Advanced Features

### JavaScript Integration
```javascript
// Interactive HTML cells can query Prolog dynamically
notebook.swish({
    ask: "emotion(State, Level)",
    ondata: function(data) {
        $("#emotion-display").text(`${data.State}: ${data.Level}`);
    }
});
```

### URL Parameters
```
# Load notebook with specific query
http://localhost:3050/?code=/data/notebooks/aseke.swinb&q=emotion(X,Y)

# Load with background knowledge
http://localhost:3050/?background=my_facts.pl&q=test_query.
```

### CSV Export
```python
# Export query results programmatically
notebook.download_csv("emotion(State, Level)", columns=["State", "Level"])
```

## 🚨 Common Mistakes (And Fixes)

### ❌ "Knowledge keeps disappearing!"
**Problem**: Using separate queries instead of notebook background cells  
**Fix**: Create notebook with background cells for persistent state

### ❌ "Consult() succeeds but predicates not found!"
**Problem**: Pengine session isolation  
**Fix**: Use background cells in notebooks, not separate file consultation

### ❌ "Tools seem broken/unresponsive!"
**Problem**: Expecting web-SWISH behavior from Docker-SWISH  
**Fix**: Use enhanced tools that leverage Docker-SWISH capabilities properly

### ❌ "Can't find my work later!"
**Problem**: Using .pl files in isolated sessions  
**Fix**: Use .swinb notebooks that persist in /data/notebooks/

## 📈 Success Patterns

### ✅ Persistent Knowledge Laboratory
```python
# 1. Create domain-specific notebook
create_notebook("biology_lab", background_knowledge=biology_facts)

# 2. Iterative knowledge building
add_background_cell("biology_lab", "new_discovery(X) :- research_result(X).")

# 3. Interactive exploration via web interface
# 4. Export results and insights
# 5. Share complete reproducible notebooks
```

### ✅ Collaborative Development
```python
# 1. Create shared notebook with team knowledge
# 2. Team members add background cells
# 3. Export/import notebooks for version control
# 4. Merge insights across team members
```

### ✅ Educational Use
```python
# 1. Create tutorial notebook with progressive examples
# 2. Students experiment with query cells
# 3. Background cells provide consistent knowledge base
# 4. Rich documentation in markdown cells
```

## 🎯 Bottom Line

**The Tools Work Great** - they just use a different (better!) architecture:

- **Docker-SWISH**: Containerized, MCP-integrated, file-persistent
- **Web-SWISH**: Browser-based, limited persistence, public server

**Use notebooks with background cells** and you get exactly the "notepad that doesn't vanish" experience you wanted! 

The persistent state issue is completely solved. 🎉

## 📚 Next Steps

1. **Try the ASEKE notebook**: `create_aseke_cognitive_notebook()`
2. **Explore the web interface**: Rich editing and visualization
3. **Build domain knowledge**: Create notebooks for your specific needs
4. **Share insights**: Export notebooks for collaboration

The enhanced tools turn Docker-SWISH into a powerful, persistent knowledge laboratory! 🚀
