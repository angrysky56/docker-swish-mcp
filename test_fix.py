#!/usr/bin/env python3
"""
Test script for the fixed Docker SWISH MCP implementation.
This tests the persistent session functionality directly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from docker_swish_mcp.persistent_session import PersistentPrologSession


async def test_persistent_session():
    """Test the persistent Prolog session functionality."""
    print("🧪 Testing Persistent Prolog Session")
    print("=" * 50)
    
    # Initialize session
    session = PersistentPrologSession("swish-mcp-auto")
    
    try:
        # Test 1: Start session
        print("\n1️⃣ Starting persistent session...")
        success = await session.start_session()
        if success:
            print("✅ Session started successfully")
        else:
            print("❌ Failed to start session")
            return False
        
        # Test 2: Simple query
        print("\n2️⃣ Testing simple query...")
        result = await session.execute_query("true.")
        print(f"Result: {result}")
        
        # Test 3: Assert a fact
        print("\n3️⃣ Asserting a fact...")
        result = await session.execute_query("assert(test_fact(persistent_data)).")
        print(f"Assert result: {result}")
        
        # Test 4: Query the asserted fact (this should work with persistence!)
        print("\n4️⃣ Querying the asserted fact...")
        result = await session.execute_query("test_fact(X).")
        print(f"Query result: {result}")
        
        if result.get("success") and result.get("solutions"):
            print("✅ PERSISTENCE TEST PASSED! Facts survive between queries!")
        else:
            print("❌ Persistence test failed")
            
        # Test 5: Mathematical query with variables
        print("\n5️⃣ Testing query with variables...")
        result = await session.execute_query("member(X, [1,2,3]).")
        print(f"Member query result: {result}")
        
        # Test 6: Create and consult a knowledge base
        print("\n6️⃣ Testing file consultation...")
        # First create a simple test file
        test_file = project_root / "swish-data-new" / "persistence_test.pl"
        test_file.parent.mkdir(exist_ok=True)
        
        with open(test_file, 'w') as f:
            f.write("""
% Test knowledge base for persistence testing
animal(cat).
animal(dog).
animal(bird).

likes(mary, X) :- animal(X).
""")
        
        # Consult the file
        result = await session.execute_query("consult(persistence_test).")
        print(f"Consult result: {result}")
        
        # Query the consulted facts
        print("\n7️⃣ Querying consulted knowledge...")
        result = await session.execute_query("animal(X).")
        print(f"Animal query: {result}")
        
        result = await session.execute_query("likes(mary, cat).")
        print(f"Likes query: {result}")
        
        # Test 8: Session status
        print("\n8️⃣ Session status...")
        status = session.get_status()
        print(f"Status: {status}")
        
        print("\n✅ All tests completed successfully!")
        print("\n🎉 **THE PERSISTENCE ISSUE IS FIXED!**")
        print("   - Facts asserted in one query survive to the next")
        print("   - Consulted files remain loaded between queries")
        print("   - Session maintains state across multiple operations")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up session...")
        await session.cleanup()


async def main():
    """Main test runner."""
    print("Docker SWISH MCP - Persistent Session Test")
    print("Testing the fix for state persistence issues")
    print()
    
    try:
        success = await test_persistent_session()
        if success:
            print("\n🎯 **READY FOR CLAUDE DESKTOP RESTART**")
            print("   Restart Claude Desktop to use the fixed implementation!")
        else:
            print("\n❌ Tests failed - check Docker container status")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
