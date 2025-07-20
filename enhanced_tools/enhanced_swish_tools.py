#!/usr/bin/env python3
"""
Enhanced SWISH-Prolog MCP Server Tools
=====================================

Improved tools that leverage SWISH notebook capabilities for better UX:
- Notebook file creation and management (.swinb files)
- Background cell persistence for knowledge retention
- Better documentation and error messaging
- Interactive HTML cell support

This addresses the core UX issues:
1. Session state persistence through background cells
2. Intuitive notebook-based interface
3. Clear documentation of Docker-SWISH behavior
4. Better discoverability and usability
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime


class EnhancedSWISHTools:
    """Enhanced SWISH tools with notebook support and better UX."""
    
    def __init__(self, data_dir: str = "/data"):
        self.data_dir = Path(data_dir)
        self.notebooks_dir = self.data_dir / "notebooks"
        self.knowledge_bases_dir = self.data_dir / "knowledge_bases"
        
        # Ensure directories exist
        self.notebooks_dir.mkdir(exist_ok=True)
        self.knowledge_bases_dir.mkdir(exist_ok=True)
    
    def create_notebook(
        self, 
        name: str, 
        title: str = None,
        description: str = None,
        background_knowledge: List[str] = None,
        initial_query: str = None
    ) -> Dict[str, str]:
        """
        Create a new SWISH notebook (.swinb) with persistent background cells.
        
        This solves the session state problem by using SWISH's background cell
        feature to maintain knowledge across query executions.
        
        Args:
            name: Notebook filename (without .swinb extension)
            title: Human-readable title for the notebook
            description: Description of the notebook's purpose
            background_knowledge: List of Prolog facts/rules for background cells
            initial_query: Default query to show in query cell
            
        Returns:
            Dict with notebook path, URL, and usage instructions
        """
        if not title:
            title = name.replace("_", " ").title()
        
        if not description:
            description = f"Interactive Prolog notebook: {title}"
        
        # Create notebook structure
        notebook = {
            "notebook": True,
            "cells": []
        }
        
        # Add markdown header cell
        header_cell = {
            "type": "markdown",
            "name": "header",
            "content": f"# {title}\n\n{description}\n\n**Created:** {datetime.now().isoformat()}\n\n---\n"
        }
        notebook["cells"].append(header_cell)
        
        # Add background program cells for persistent knowledge
        if background_knowledge:
            for i, knowledge in enumerate(background_knowledge):
                bg_cell = {
                    "type": "program",
                    "name": f"background_{i+1}",
                    "background": True,  # This makes the cell persistent!
                    "content": f"% Background Knowledge Cell {i+1}\n% This knowledge persists across all queries in this notebook\n\n{knowledge}\n"
                }
                notebook["cells"].append(bg_cell)
        
        # Add instructions cell
        instructions = """## How to Use This Notebook

**Background Cells**: The cells marked with 🔒 contain persistent knowledge that's available to all queries.

**Query Cells**: Use the ▶️ button to run queries against the background knowledge.

**Adding Knowledge**: Edit background cells to add new facts and rules.

**Tip**: Knowledge in background cells persists across all queries in this notebook, solving the session state issue!"""
        
        instruction_cell = {
            "type": "markdown", 
            "name": "instructions",
            "content": instructions
        }
        notebook["cells"].append(instruction_cell)
        
        # Add initial query cell if provided
        if initial_query:
            query_cell = {
                "type": "query",
                "name": "initial_query",
                "content": initial_query
            }
            notebook["cells"].append(query_cell)
        
        # Save notebook file
        notebook_path = self.notebooks_dir / f"{name}.swinb"
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "notebook_path": str(notebook_path),
            "notebook_name": f"{name}.swinb",
            "title": title,
            "web_url": f"http://localhost:3050/?code={notebook_path}",
            "usage_instructions": f"""
📓 Notebook created successfully!

**File**: {notebook_path}
**Web Access**: http://localhost:3050/?code={notebook_path}

🔑 **Key Features**:
- Background cells maintain state across queries
- Markdown cells for documentation  
- Interactive query cells
- Persistent knowledge base

💡 **Usage Tips**:
1. Edit background cells to add permanent knowledge
2. Use query cells to test and explore
3. Add markdown cells for documentation
4. All background knowledge persists automatically!

This solves the session state problem you identified! 🎯
"""
        }
    
    def add_background_cell(
        self, 
        notebook_name: str, 
        knowledge: str, 
        cell_name: str = None
    ) -> Dict[str, str]:
        """Add a new background cell to existing notebook."""
        notebook_path = self.notebooks_dir / f"{notebook_name}.swinb"
        
        if not notebook_path.exists():
            return {
                "status": "error",
                "message": f"Notebook {notebook_name} not found. Available notebooks: {self.list_notebooks()}"
            }
        
        # Load existing notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Generate cell name if not provided
        if not cell_name:
            bg_count = len([c for c in notebook["cells"] if c.get("background", False)])
            cell_name = f"background_{bg_count + 1}"
        
        # Add new background cell
        new_cell = {
            "type": "program",
            "name": cell_name,
            "background": True,
            "content": f"% Background Knowledge: {cell_name}\n\n{knowledge}\n"
        }
        
        notebook["cells"].append(new_cell)
        
        # Save updated notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "message": f"Added background cell '{cell_name}' to {notebook_name}.swinb",
            "cell_name": cell_name,
            "notebook_path": str(notebook_path)
        }
    
    def list_notebooks(self) -> List[Dict[str, str]]:
        """List all available SWISH notebooks."""
        notebooks = []
        for notebook_file in self.notebooks_dir.glob("*.swinb"):
            try:
                with open(notebook_file, 'r', encoding='utf-8') as f:
                    notebook = json.load(f)
                
                # Extract title and description from first markdown cell
                title = notebook_file.stem
                description = "SWISH Notebook"
                
                for cell in notebook.get("cells", []):
                    if cell.get("type") == "markdown" and "content" in cell:
                        content = cell["content"]
                        if content.startswith("#"):
                            lines = content.split("\n")
                            title = lines[0].replace("#", "").strip()
                            if len(lines) > 2:
                                description = lines[2].strip()
                        break
                
                notebooks.append({
                    "name": notebook_file.stem,
                    "filename": notebook_file.name,
                    "title": title,
                    "description": description,
                    "path": str(notebook_file),
                    "url": f"http://localhost:3050/?code={notebook_file}",
                    "modified": datetime.fromtimestamp(notebook_file.stat().st_mtime).isoformat()
                })
            except Exception as e:
                notebooks.append({
                    "name": notebook_file.stem,
                    "filename": notebook_file.name,
                    "title": "Error loading notebook",
                    "description": f"Error: {str(e)}",
                    "path": str(notebook_file),
                    "error": True
                })
        
        return sorted(notebooks, key=lambda x: x.get("modified", ""), reverse=True)
    
    def create_aseke_cognitive_notebook(self) -> Dict[str, str]:
        """Create a specialized notebook for ASEKE cognitive architecture experiments."""
        
        aseke_background = [
            """% ASEKE Cognitive Architecture - Core Knowledge Base
% Emotional State Algorithms (ESA) - Plutchik's Emotions
emotion(joy).
emotion(trust). 
emotion(fear).
emotion(surprise).
emotion(sadness).
emotion(disgust).
emotion(anger).
emotion(anticipation).

% Emotional state management
emotional_state(curiosity, high).
emotional_state(engagement, medium).
emotional_state(confidence, growing).

% Meta-cognitive monitoring
meta_state(system_learning).
meta_state(knowledge_integration).
meta_state(pattern_recognition).""",

            """% Knowledge Substrate and Information Structures
% Knowledge entities
knowledge_entity(concept).
knowledge_entity(fact).
knowledge_entity(rule).
knowledge_entity(theory).
knowledge_entity(belief).

% Domain knowledge example: Photosynthesis
process(photosynthesis).
location(photosynthesis, chloroplast).
input_molecule(photosynthesis, carbon_dioxide).
input_molecule(photosynthesis, water).
input_molecule(photosynthesis, light_energy).
output_molecule(photosynthesis, glucose).
output_molecule(photosynthesis, oxygen).

% Sub-processes
subprocess(photosynthesis, light_reactions).
subprocess(photosynthesis, calvin_cycle).
location(light_reactions, thylakoid_membrane).
location(calvin_cycle, stroma).""",

            """% Curiosity Loop Implementation
% Knowledge gap detection
knowledge_gap(calvin_cycle, key_enzyme).
knowledge_gap(photosynthesis, efficiency_rate).
knowledge_gap(light_reactions, electron_transport).

% Gap detection predicate
detect_knowledge_gap(Domain, Gap) :-
    knowledge_gap(Domain, Gap),
    \\+ has_knowledge(Domain, Gap).

% Current knowledge state
has_knowledge(photosynthesis, process_type).
has_knowledge(photosynthesis, location).
has_knowledge(photosynthesis, inputs).
has_knowledge(photosynthesis, outputs).

% Inquiry generation
generate_inquiry(Domain, Gap, Query) :-
    detect_knowledge_gap(Domain, Gap),
    atomic_list_concat(['What is the', Gap, 'for', Domain, '?'], ' ', Query)."""
        ]
        
        return self.create_notebook(
            name="aseke_cognitive_architecture",
            title="ASEKE Cognitive Architecture Laboratory",
            description="Interactive notebook for exploring Adaptive Socio-Emotional Knowledge Ecosystem concepts with persistent state management.",
            background_knowledge=aseke_background,
            initial_query="emotional_state(State, Level)."
        )
    
    def get_usage_instructions(self) -> str:
        """Comprehensive usage instructions for the enhanced SWISH tools."""
        return """
🚀 **Enhanced SWISH-Prolog MCP Server - Usage Guide**

## Key Differences from Web SWISH

**Docker-SWISH (This System)**:
- ✅ Containerized execution environment
- ✅ MCP integration for AI assistants  
- ✅ Persistent file storage in /data
- ✅ Background cells maintain state
- ⚠️  Different session model than web SWISH

**Web SWISH (swish.swi-prolog.org)**:
- ✅ Browser-based interface
- ✅ Direct pengine interaction
- ⚠️  Public server limitations
- ⚠️  No local file integration

## Solving the Session State Problem

**The Issue**: In Docker-SWISH, predicates don't persist between separate queries due to pengine isolation.

**The Solution**: Use SWISH notebooks with background cells!

### Background Cells = Persistent Knowledge

```prolog
% Background Cell (persists across queries)
person(alice).
person(bob).
likes(alice, prolog).
likes(bob, chocolate).
```

### Query Cells = Interactive Exploration

```prolog
% Query Cell (uses background knowledge)
?- likes(X, Y).
```

## Enhanced Tool Workflow

### 1. Create Persistent Notebooks
```python
# Create notebook with background knowledge
create_notebook("my_experiment", 
               background_knowledge=["fact(a).", "rule(X) :- fact(X)."])
```

### 2. Add Knowledge Incrementally  
```python
# Add new background cell
add_background_cell("my_experiment", "new_fact(b).")
```

### 3. Use Web Interface
- Access: http://localhost:3050/?code=/data/notebooks/my_experiment.swinb
- Edit background cells to modify persistent knowledge
- Use query cells for interactive exploration

## Best Practices

### ✅ Do This:
- Use notebooks (.swinb) for persistent work
- Put core knowledge in background cells  
- Use markdown cells for documentation
- Access via web interface for rich editing

### ❌ Avoid This:
- Expecting predicates to persist across separate MCP queries
- Using .pl files for interactive work (they don't persist state)
- Forgetting to mark cells as "background" for persistence

## Example Workflow: ASEKE Cognitive Architecture

1. **Create specialized notebook**:
   ```python
   create_aseke_cognitive_notebook()
   ```

2. **Access web interface**:
   - Open: http://localhost:3050/?code=/data/notebooks/aseke_cognitive_architecture.swinb
   
3. **Interactive exploration**:
   - Background cells contain persistent ASEKE knowledge
   - Query cells test emotional states, knowledge gaps, curiosity loops
   - Add new background cells for expanding the architecture

4. **Document insights**:
   - Use markdown cells to document discoveries
   - Export notebook for sharing/archiving

## Troubleshooting

**Problem**: "Unknown procedure" errors
**Solution**: Ensure knowledge is in background cells, not regular program cells

**Problem**: Knowledge disappears between queries  
**Solution**: Use notebooks with background cells instead of separate queries

**Problem**: Can't find notebooks
**Solution**: Check /data/notebooks/ directory, use list_notebooks() 

## Integration with Cognitive Architectures

This enhanced system is particularly powerful for:
- **ASEKE**: Persistent emotional states and knowledge management
- **Logic Programming Research**: Systematic knowledge base development  
- **Educational Use**: Interactive tutorials with persistent examples
- **Collaborative Development**: Shareable notebooks with embedded documentation

The background cell persistence solves your original "notepad that doesn't vanish" requirement! 🎯
"""


# Export enhanced tools class for MCP server integration
__all__ = ['EnhancedSWISHTools']
