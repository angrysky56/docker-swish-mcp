"""
Docker SWISH MCP Server

A Model Context Protocol server for managing Docker SWISH containers
and interacting with SWI-Prolog knowledge bases.

This package provides:
- Docker container management for SWISH
- Prolog query execution via SWISH API
- Knowledge base file management
- Authentication configuration
- Prolog programming assistance prompts
"""

from .main import mcp

__version__ = "0.1.0"
__all__ = ["mcp"]
