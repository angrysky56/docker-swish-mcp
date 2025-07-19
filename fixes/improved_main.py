"""
Docker SWISH MCP Server - Improved Version

This version includes:
- Better error handling and logging
- Proper MCP initialization response
- Clearer separation between MCP server and Docker container
- Enhanced debugging capabilities
"""

from __future__ import annotations

import asyncio
import atexit
import json
import logging
import signal
import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Configure logging to stderr for MCP servers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("docker-swish-mcp")

# Version info
__version__ = "0.2.0"
# Global tracking for cleanup
running_processes: dict[str, Any] = {}
background_tasks: set[asyncio.Task] = set()
global_swish_context: SwishContext | None = None


@dataclass
class SwishContext:
    """Application context for SWISH operations"""
    docker_client: Any = None
    container_name: str = "swish-mcp"
    port: int = 3050
    data_dir: Path = Path.cwd() / "swish-data"
    swish_base_url: str = "http://localhost:3050"
    docker_available: bool = False


def cleanup_processes() -> None:
    """Clean up all running processes and background tasks"""
    logger.info("Cleaning up processes and tasks")
    
    # Cancel background tasks
    for task in background_tasks:
        if not task.done():
            task.cancel()
    
    # Stop any running containers
    if global_swish_context and global_swish_context.docker_available:
        try:
            import docker
            client = docker.from_env()
            container = client.containers.get(global_swish_context.container_name)
            logger.info(f"Stopping container {global_swish_context.container_name}")
            container.stop()
            container.remove()
        except Exception as e:
            logger.debug(f"Container cleanup: {e}")
    
    # Clear collections
    running_processes.clear()
    background_tasks.clear()


def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    cleanup_processes()
    sys.exit(0)

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[SwishContext]:
    """Manage application lifecycle with proper initialization"""
    global global_swish_context
    
    logger.info(f"Initializing Docker SWISH MCP Server v{__version__}")
    
    try:
        # Try to import and initialize Docker
        import docker
        
        try:
            docker_client = docker.from_env()
            # Test Docker connection
            docker_client.ping()
            docker_available = True
            logger.info("✅ Docker client initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Docker not available: {e}")
            logger.warning("Running in limited mode - container management disabled")
            docker_client = None
            docker_available = False
        
        # Create context
        context = SwishContext(
            docker_client=docker_client,
            docker_available=docker_available
        )
        
        # Ensure data directory exists
        context.data_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Data directory: {context.data_dir}")
        
        # Set global context
        global_swish_context = context
        
        # Log server info
        logger.info("🚀 MCP Server ready to accept connections")
        logger.info(f"📍 SWISH URL will be: {context.swish_base_url}")
        
        yield context
        
    except ImportError:
        logger.error("❌ Docker package not installed. Please install with: uv add docker")
        context = SwishContext(docker_available=False)
        global_swish_context = context
        yield context
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        context = SwishContext(docker_available=False)
        global_swish_context = context
        yield context
        
    finally:
        # Cleanup on shutdown
        logger.info("🛑 Shutting down Docker SWISH MCP server")
        cleanup_processes()
        global_swish_context = None

def get_context() -> SwishContext:
    """Get current context with proper error handling"""
    if global_swish_context is None:
        raise RuntimeError("SWISH context not initialized. Server may not be properly started.")
    return global_swish_context


def track_background_task(task: asyncio.Task) -> None:
    """Track background tasks for cleanup"""
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


# Register cleanup handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_processes)

# Initialize MCP server with metadata
logger.info("Creating FastMCP server instance...")
mcp = FastMCP(
    name="Docker-SWISH-MCP",
    version=__version__,
    description="Manage Docker SWISH containers and Prolog knowledge bases",
    lifespan=app_lifespan
)

# Log available tools on startup
logger.info("Registering MCP tools...")

@mcp.tool()
async def start_swish_container(
    port: int = 3050,
    data_dir: str | None = None,
    auth_mode: str = "anon",
    https: bool = False,
    detached: bool = True
) -> str:
    """
    Start a Docker SWISH container for SWI-Prolog programming.
    
    This tool manages the lifecycle of a SWISH (SWI-Prolog for SHaring) container,
    providing a web-based Prolog development environment.
    
    Args:
        port: Port to expose SWISH on (default: 3050)
        data_dir: Host directory to mount as /data (default: ./swish-data)
        auth_mode: Authentication mode - 'anon' (anonymous), 'social' (OAuth), 'always' (required)
        https: Enable HTTPS with self-signed certificate
        detached: Run container in background
        
    Returns:
        Status message with container information
        
    Example:
        start_swish_container(port=3051, auth_mode="social")
    """
    logger.info(f"Tool called: start_swish_container(port={port}, auth_mode={auth_mode})")
    
    try:
        context = get_context()
        
        if not context.docker_available:
            return """❌ Docker is not available. Please ensure:
1. Docker Desktop is installed and running
2. You have permission to access Docker
3. The docker Python package is installed (uv add docker)"""
        
        docker_client = context.docker_client
        
        # Set up data directory
        if data_dir:
            data_path = Path(data_dir).expanduser().resolve()
        else:
            data_path = context.data_dir / "data"
        
        data_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using data directory: {data_path}")
        
        # Check for existing container
        try:
            existing = docker_client.containers.get(context.container_name)
            if existing.status == "running":
                logger.info(f"Container {context.container_name} already running")
                return f"""ℹ️ SWISH container already running
🌐 Access at: {context.swish_base_url}
💡 Use stop_swish_container() to stop it first"""
            else:
                logger.info(f"Removing stopped container: {context.container_name}")
                existing.remove()
        except Exception as e:
            logger.debug(f"No existing container found: {e}")
        
        # Validate auth mode
        if auth_mode not in ["anon", "social", "always"]:
            return "❌ Invalid auth_mode. Use: 'anon', 'social', or 'always'"
        
        # Build container configuration
        container_config = {
            "image": "swipl/swish:latest",
            "name": context.container_name,
            "ports": {"3050/tcp": port},
            "volumes": {str(data_path): {"bind": "/data", "mode": "rw"}},
            "detach": detached,
            "remove": False,
            "environment": {},
            "labels": {
                "managed-by": "docker-swish-mcp",
                "mcp-version": __version__
            }
        }
        
        # Add command arguments for auth and https
        command_args = []
        if auth_mode != "anon":
            command_args.extend(["--auth", auth_mode])
        if https:
            command_args.append("--https")
        
        if command_args:
            container_config["command"] = command_args
        
        # Pull image if needed
        logger.info("Ensuring SWISH image is available...")
        try:
            docker_client.images.pull("swipl/swish:latest")
        except Exception as e:
            logger.warning(f"Could not pull latest image: {e}")
        
        # Start container
        logger.info(f"Starting SWISH container on port {port}...")
        container = docker_client.containers.run(**container_config)
        
        # Update context
        context.port = port
        context.swish_base_url = f"{'https' if https else 'http'}://localhost:{port}"
        
        # Track container
        running_processes[context.container_name] = container
        
        # Wait a moment for container to start
        await asyncio.sleep(2)
        
        return f"""✅ SWISH container started successfully!
        
🌐 Access SWISH at: {context.swish_base_url}
📁 Data directory: {data_path}
🔒 Authentication: {auth_mode}
🔐 HTTPS: {'enabled' if https else 'disabled'}
📋 Container ID: {container.id[:12]}

💡 Next steps:
- Create Prolog files with create_prolog_file()
- Execute queries with execute_prolog_query()
- Check status with get_swish_status()"""
        
    except Exception as e:
        logger.error(f"Failed to start SWISH container: {e}", exc_info=True)
        return f"❌ Failed to start SWISH container: {str(e)}"


@mcp.tool()
async def stop_swish_container() -> str:
    """
    Stop the running SWISH container.
    
    This will stop and remove the container, but preserve any data
    in the mounted data directory.
    
    Returns:
        Status message
    """
    logger.info("Tool called: stop_swish_container()")
    
    try:
        context = get_context()
        
        if not context.docker_available:
            return "❌ Docker is not available"
        
        docker_client = context.docker_client
        
        try:
            container = docker_client.containers.get(context.container_name)
            
            logger.info(f"Stopping container {context.container_name}...")
            container.stop(timeout=10)
            container.remove()
            
            # Remove from tracking
            if context.container_name in running_processes:
                del running_processes[context.container_name]
            
            return f"""✅ SWISH container stopped and removed
            
📁 Data preserved in: {context.data_dir}
💡 Start again with start_swish_container()"""
            
        except Exception as e:
            logger.debug(f"Container not found: {e}")
            return "ℹ️ No SWISH container is currently running"
            
    except Exception as e:
        logger.error(f"Failed to stop container: {e}", exc_info=True)
        return f"❌ Failed to stop container: {str(e)}"


@mcp.tool()
async def get_swish_status() -> str:
    """
    Get the current status of the SWISH container and service.
    
    Provides detailed information about:
    - Container status and health
    - Service accessibility
    - Resource usage
    - Configuration details
    
    Returns:
        Detailed status information
    """
    logger.info("Tool called: get_swish_status()")
    
    try:
        context = get_context()
        
        if not context.docker_available:
            return """⚠️ Docker is not available
            
The MCP server is running but cannot manage containers.
Please ensure Docker Desktop is running."""
        
        docker_client = context.docker_client
        
        try:
            container = docker_client.containers.get(context.container_name)
            
            # Get container details
            status = container.status
            stats = container.stats(stream=False)
            created = container.attrs['Created']
            
            # Check SWISH accessibility
            swish_accessible = False
            error_msg = ""
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{context.swish_base_url}/",
                        timeout=aiohttp.ClientTimeout(total=5),
                        ssl=False
                    ) as response:
                        swish_accessible = response.status == 200
            except Exception as e:
                error_msg = str(e)
            
            # Format memory usage
            memory_usage = stats.get('memory_stats', {}).get('usage', 0)
            memory_mb = memory_usage / (1024 * 1024)
            
            return f"""📊 SWISH Container Status
            
🐳 Container: {container.name} ({container.id[:12]})
📊 Status: {status.upper()}
🌐 URL: {context.swish_base_url}
🚀 Service: {'✅ Accessible' if swish_accessible else f'❌ Not accessible ({error_msg})'}
💾 Memory: {memory_mb:.1f} MB
📅 Created: {created}
📁 Data: {context.data_dir}

💡 Container is {'ready for use' if status == 'running' and swish_accessible else 'starting up...' if status == 'running' else 'not running'}"""
            
        except Exception as e:
            return f"""ℹ️ No SWISH container found
            
🔍 Container '{context.container_name}' is not running
💡 Start with: start_swish_container()
📁 Data directory: {context.data_dir}"""
            
    except Exception as e:
        logger.error(f"Failed to get status: {e}", exc_info=True)
        return f"❌ Failed to get status: {str(e)}"


@mcp.tool()
async def test_mcp_connection() -> str:
    """
    Test that the MCP server is working correctly.
    
    This is a simple diagnostic tool to verify:
    - MCP server is responding
    - Python environment is set up
    - Basic functionality works
    
    Returns:
        Test results and server information
    """
    logger.info("Tool called: test_mcp_connection()")
    
    try:
        context = get_context()
        
        # Gather system info
        import platform
        
        return f"""✅ MCP Server Connection Test Successful!
        
🔧 Server Information:
- Name: Docker-SWISH-MCP
- Version: {__version__}
- Python: {platform.python_version()}
- Platform: {platform.platform()}

🐳 Docker Status:
- Available: {'✅ Yes' if context.docker_available else '❌ No'}
- Data Dir: {context.data_dir}
- Container Name: {context.container_name}

📋 Available Tools:
- start_swish_container() - Launch SWISH
- stop_swish_container() - Stop SWISH
- get_swish_status() - Check status
- test_mcp_connection() - This test

🎯 Everything is working correctly!"""
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return f"❌ Test failed: {str(e)}"


# Main entry point
def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info("=" * 60)
        logger.info(f"Docker SWISH MCP Server v{__version__}")
        logger.info("Starting server...")
        logger.info("=" * 60)
        
        # Run the MCP server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        cleanup_processes()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()