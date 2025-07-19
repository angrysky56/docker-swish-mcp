#!/usr/bin/env python3
"""
Docker connectivity test for SWISH MCP Server

Tests Docker availability and permissions.
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🐳 Docker Connectivity Test")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Docker command exists
    tests_total += 1
    print("\n1️⃣ Checking if Docker is installed...")
    success, stdout, stderr = run_command("which docker")
    if success:
        print(f"✅ Docker found at: {stdout.strip()}")
        tests_passed += 1
    else:
        print("❌ Docker command not found")
        print("   Install Docker Desktop from: https://www.docker.com/products/docker-desktop")
    
    # Test 2: Docker daemon running
    tests_total += 1
    print("\n2️⃣ Checking if Docker daemon is running...")
    success, stdout, stderr = run_command("docker info > /dev/null 2>&1")
    if success:
        print("✅ Docker daemon is running")
        tests_passed += 1
    else:
        print("❌ Docker daemon is not running")
        print("   Start Docker Desktop application")
    
    # Test 3: Docker permissions
    tests_total += 1
    print("\n3️⃣ Checking Docker permissions...")
    success, stdout, stderr = run_command("docker ps")
    if success:
        print("✅ Docker permissions OK")
        tests_passed += 1
    else:
        print("❌ Docker permission denied")
        if "permission denied" in stderr.lower():
            print("   Add your user to docker group:")
            print("   sudo usermod -aG docker $USER")
            print("   Then logout and login again")
    
    # Test 4: Pull test image
    tests_total += 1
    print("\n4️⃣ Testing Docker connectivity...")
    success, stdout, stderr = run_command("docker pull hello-world")
    if success:
        print("✅ Docker can pull images")
        tests_passed += 1
    else:
        print("❌ Cannot pull Docker images")
        print("   Check your internet connection")
    
    # Test 5: Check for SWISH image
    tests_total += 1
    print("\n5️⃣ Checking for SWISH image...")
    success, stdout, stderr = run_command("docker images swipl/swish --format '{{.Repository}}:{{.Tag}}'")
    if success and stdout.strip():
        print(f"✅ SWISH image found: {stdout.strip()}")
        tests_passed += 1
    else:
        print("ℹ️ SWISH image not found (will be pulled on first use)")
        tests_passed += 1  # This is OK
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("✅ All tests passed! Docker is ready for SWISH MCP.")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
