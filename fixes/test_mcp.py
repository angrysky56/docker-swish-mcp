#!/usr/bin/env python3
"""
Diagnostic script for Docker SWISH MCP Server

Run this to test the MCP server functionality without Claude Desktop.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docker_swish_mcp.main import mcp, test_mcp_connection, get_swish_status, start_swish_container


async def run_diagnostics():
    """Run diagnostic tests on the MCP server."""
    print("🔍 Docker SWISH MCP Server Diagnostics")
    print("=" * 60)
    
    # Test 1: MCP Connection
    print("\n1️⃣ Testing MCP Connection...")
    result = await test_mcp_connection()
    print(result)
    
    # Test 2: Check SWISH Status
    print("\n2️⃣ Checking SWISH Status...")
    result = await get_swish_status()
    print(result)
    
    # Test 3: List available tools
    print("\n3️⃣ Available MCP Tools:")
    tools = mcp.list_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\n✅ Diagnostics complete!")
    print("\n💡 To test container management:")
    print("  1. Run: await start_swish_container()")
    print("  2. Visit: http://localhost:3050")
    print("  3. Run: await stop_swish_container()")


async def interactive_test():
    """Run an interactive test session."""
    print("\n🚀 Interactive Test Mode")
    print("You can now test MCP tools interactively.")
    print("Example commands:")
    print("  await start_swish_container()")
    print("  await get_swish_status()")
    print("  await stop_swish_container()")
    print("\nPress Ctrl+C to exit")
    
    # Keep the event loop running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n👋 Exiting interactive mode")


async def main():
    """Main entry point for diagnostics."""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_test()
    else:
        await run_diagnostics()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Diagnostics interrupted")
