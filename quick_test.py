#!/usr/bin/env python3
"""
Quick test of the simplified persistent session.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from docker_swish_mcp.simple_session import SimplePrologSession


async def quick_test():
    """Quick test of simplified session."""
    print("🧪 Testing Simplified Session")
    print("=" * 40)
    
    session = SimplePrologSession("swish-mcp-auto")
    
    try:
        # Test 1: Start session
        print("1️⃣ Starting session...")
        if await session.start_session():
            print("✅ Session started")
        else:
            print("❌ Session failed")
            return
        
        # Test 2: Simple test
        print("2️⃣ Testing simple query...")
        result = await session.execute_query("true.")
        print(f"Result: {result}")
        
        # Test 3: Assert and query (the persistence test!)
        print("3️⃣ Testing persistence...")
        result1 = await session.execute_query("assert(test_works(yes)).")
        print(f"Assert: {result1}")
        
        result2 = await session.execute_query("test_works(X).")
        print(f"Query: {result2}")
        
        if result2.get("success"):
            print("🎉 PERSISTENCE WORKS!")
        else:
            print("❌ Still no persistence")
            
    finally:
        await session.cleanup()


if __name__ == "__main__":
    asyncio.run(quick_test())
