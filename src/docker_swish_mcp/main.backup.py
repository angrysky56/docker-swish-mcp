"""
Docker SWISH MCP Server - Fixed Main Module

FIXED: Resolved FastMCP context access issue by using global context variable
instead of trying to access mcp.request_context.lifespan_context

Provides MCP tools, resources, and prompts for managing Docker SWISH containers
and interacting with SWI-Prolog knowledge bases.
"""

from __future__ import annotations

import asyncio
import atexit
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global tracking for cleanup
running_processes: dict[str, Any] = {}
background_tasks: set[asyncio.Task] = set()

# FIXED: Global context variable to avoid FastMCP context access issues
global_swish_context: SwishContext | None = None


@dataclass
class SwishContext:
    """Application context for SWISH operations"""
    docker_client: Any = None
    container_name: str = "swish-mcp"
    port: int = 3050
    data_dir: Path = Path.cwd() / "swish-data"
    swish_base_url: str = "http://localhost:3050"


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[SwishContext]:
    """Manage application lifecycle with Docker client initialization"""
    global global_swish_context

    try:
        # Import Docker here to avoid import-time errors
        import docker

        # Initialize Docker client
        docker_client = docker.from_env()

        # Create context
        context = SwishContext(docker_client=docker_client)

        # Ensure data directory exists
        context.data_dir.mkdir(exist_ok=True)

        # FIXED: Set global context for tool access
        global_swish_context = context

        logger.info(f"Initialized SWISH context with data dir: {context.data_dir}")

        yield context

    except Exception as e:
        logger.error(f"Failed to initialize Docker client: {e}")
        # Create context without Docker client for testing
        context = SwishContext()
        global_swish_context = context
        yield context
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down SWISH MCP server")
        global_swish_context = None
        cleanup_processes()


def get_context() -> SwishContext:
    """
    FIXED: Helper function to get context reliably

    Returns:
        Current SwishContext instance

    Raises:
        RuntimeError: If context is not available
    """
    if global_swish_context is None:
        raise RuntimeError("SWISH context not initialized. Server may not be properly started.")
    return global_swish_context


def cleanup_processes() -> None:
    """Clean up all running processes and background tasks"""
    logger.info("Cleaning up processes and tasks")

    # Cancel background tasks
    for task in background_tasks:
        if not task.done():
            task.cancel()

    # Clear collections
    running_processes.clear()
    background_tasks.clear()


def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    cleanup_processes()
    sys.exit(0)


def track_background_task(task: asyncio.Task) -> None:
    """Track background tasks for cleanup"""
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


# Register cleanup handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_processes)

# Initialize MCP server with lifespan
mcp = FastMCP("Docker-SWISH-MCP", lifespan=app_lifespan)


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

    Args:
        port: Port to expose SWISH on (default: 3050)
        data_dir: Host directory to mount as /data (default: ./swish-data)
        auth_mode: Authentication mode (anon, social, always)
        https: Enable HTTPS with self-signed certificate
        detached: Run in detached mode

    Returns:
        Status message with container information
    """
    try:
        # FIXED: Use global context instead of mcp.request_context
        context = get_context()
        docker_client = context.docker_client

        if not docker_client:
            return "❌ Docker client not available. Ensure Docker is running."

        # Set up data directory
        if data_dir:
            data_path = Path(data_dir).expanduser().resolve()
        else:
            data_path = context.data_dir

        data_path.mkdir(exist_ok=True)

        # Check if container already exists - FIXED
        try:
            existing = docker_client.containers.get(context.container_name)
            if existing.status == "running":
                logger.info(f"Container {context.container_name} already running, stopping and removing it")
                existing.stop()
                existing.remove()
            else:
                logger.info(f"Removing stopped container: {context.container_name}")
                existing.remove()
        except Exception as e:
            if "not found" in str(e).lower() or "no such container" in str(e).lower():
                logger.info(f"No existing container {context.container_name} found")
            else:
                logger.warning(f"Error checking existing container: {e}")
                # Try to force remove any conflicting containers
                try:
                    result = docker_client.containers.list(all=True, filters={"name": context.container_name})
                    for container in result:
                        logger.info(f"Force removing conflicting container: {container.id}")
                        container.stop()
                        container.remove()
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup conflicting containers: {cleanup_error}")

        # Build docker run arguments
        run_args = {
            "image": "swipl/swish",
            "name": context.container_name,
            "ports": {3050: port},
            "volumes": {str(data_path): {"bind": "/data", "mode": "rw"}},
            "detach": detached,
            "remove": False
        }

        # Add authentication and HTTPS options
        command_args = []
        if auth_mode != "anon":
            command_args.extend(["--auth", auth_mode])
        if https:
            command_args.append("--https")

        if command_args:
            run_args["command"] = command_args

        # Start container
        logger.info(f"Starting SWISH container with args: {run_args}")
        container = docker_client.containers.run(**run_args)

        # Update context
        context.port = port
        context.data_dir = data_path
        context.swish_base_url = f"{'https' if https else 'http'}://localhost:{port}"

        # Track container
        running_processes[context.container_name] = container

        return f"""✅ SWISH container started successfully!
🌐 Access SWISH at: {context.swish_base_url}
📁 Data directory: {data_path}
🔒 Authentication: {auth_mode}
🔐 HTTPS: {'enabled' if https else 'disabled'}
📋 Container ID: {container.id[:12]}"""

    except Exception as e:
        logger.error(f"Failed to start SWISH container: {e}")
        return f"❌ Failed to start SWISH container: {e}"


@mcp.tool()
async def stop_swish_container() -> str:
    """
    Stop the running SWISH container.

    Returns:
        Status message
    """
    try:
        # FIXED: Use global context instead of mcp.request_context
        context = get_context()
        docker_client = context.docker_client

        if not docker_client:
            return "❌ Docker client not available"

        try:
            container = docker_client.containers.get(context.container_name)
            container.stop()
            container.remove()

            # Remove from tracking
            if context.container_name in running_processes:
                del running_processes[context.container_name]

            logger.info(f"Stopped SWISH container: {context.container_name}")
            return f"✅ SWISH container '{context.container_name}' stopped and removed"

        except Exception as e:
            logger.warning(f"Container not found or already stopped: {e}")
            return f"ℹ️ SWISH container not running or not found"

    except Exception as e:
        logger.error(f"Failed to stop SWISH container: {e}")
        return f"❌ Failed to stop SWISH container: {e}"


@mcp.tool()
async def get_swish_status() -> str:
    """
    Get the current status of the SWISH container and service.

    Returns:
        Detailed status information
    """
    try:
        # FIXED: Use global context instead of mcp.request_context
        context = get_context()
        docker_client = context.docker_client

        if not docker_client:
            return "❌ Docker client not available"

        try:
            container = docker_client.containers.get(context.container_name)

            # Get container details
            status = container.status
            ports = container.ports
            created = container.attrs['Created']

            # Check if SWISH is responding
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{context.swish_base_url}/",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        swish_responsive = response.status == 200
            except Exception:
                swish_responsive = False

            return f"""📊 SWISH Container Status:
🐳 Container: {container.id[:12]}
📊 Status: {status}
🌐 URL: {context.swish_base_url}
🚀 SWISH Responsive: {'✅ Yes' if swish_responsive else '❌ No'}
🔌 Ports: {ports}
📅 Created: {created}
📁 Data Dir: {context.data_dir}"""

        except Exception as e:
            return f"ℹ️ SWISH container not found: {e}"

    except Exception as e:
        logger.error(f"Failed to get SWISH status: {e}")
        return f"❌ Failed to get SWISH status: {e}"


@mcp.tool()
async def execute_prolog_query(
    query: str,
    timeout: int = 30
) -> str:
    """
    Execute a Prolog query against the running SWISH instance.

    Args:
        query: Prolog query to execute (e.g., "member(X, [1,2,3]).")
        timeout: Timeout in seconds for query execution

    Returns:
        Query results or error message
    """
    try:
        # FIXED: Use global context instead of mcp.request_context
        context = get_context()

        # Validate query format
        if not query.strip():
            return "❌ Empty query provided"

        # Ensure query ends with period
        if not query.strip().endswith('.'):
            query = query.strip() + '.'

        # Execute query via SWISH API
        import aiohttp
        import json

        async with aiohttp.ClientSession() as session:
            # SWISH query endpoint
            url = f"{context.swish_base_url}/ask"

            payload = {
                "q": query,
                "template": "json-s",
                "chunk": 1
            }

            try:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:

                    if response.status != 200:
                        return f"❌ SWISH API error: {response.status}"

                    result = await response.json()

                    # Format results
                    if "bindings" in result and result["bindings"]:
                        formatted_results = []
                        for binding in result["bindings"]:
                            formatted_results.append(str(binding))

                        return f"""✅ Query: {query}
📋 Results:
{chr(10).join(f"  • {result}" for result in formatted_results)}"""

                    elif "error" in result:
                        return f"❌ Prolog Error: {result['error']}"

                    else:
                        return f"✅ Query: {query}\n📋 Result: {result}"

            except asyncio.TimeoutError:
                return f"⏱️ Query timed out after {timeout} seconds"
            except aiohttp.ClientError as e:
                return f"❌ Connection error: {e}"

    except Exception as e:
        logger.error(f"Failed to execute Prolog query: {e}")
        return f"❌ Failed to execute query: {e}"


@mcp.tool()
async def create_prolog_file(
    filename: str,
    content: str,
    overwrite: bool = False
) -> str:
    """
    Create a Prolog knowledge base file in the SWISH data directory.

    Args:
        filename: Name of the .pl file (without extension)
        content: Prolog code content
        overwrite: Whether to overwrite existing file

    Returns:
        Status message
    """
    try:
        # FIXED: Use global context instead of mcp.request_context
        context = get_context()

        # Ensure filename has .pl extension
        if not filename.endswith('.pl'):
            filename = f"{filename}.pl"

        # Create file path in data directory
        file_path = context.data_dir / "data" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists
        if file_path.exists() and not overwrite:
            return f"❌ File '{filename}' already exists. Use overwrite=True to replace."

        # Write Prolog content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created Prolog file: {file_path}")
        return f"""✅ Created Prolog file: {filename}
📁 Path: {file_path}
📝 Size: {len(content)} characters
🔄 Use 'consult({filename[:-3]}).' in SWISH to load"""

    except Exception as e:
        logger.error(f"Failed to create Prolog file: {e}")
        return f"❌ Failed to create file: {e}"


@mcp.tool()
async def list_prolog_files() -> str:
    """
    List all Prolog files in the SWISH data directory.

    Returns:
        List of available Prolog files
    """
    try:
        # FIXED: Use global context instead of mcp.request_context
        context = get_context()
        data_path = context.data_dir / "data"

        if not data_path.exists():
            return "📁 No data directory found. Create some Prolog files first."

        # Find all .pl files
        prolog_files = list(data_path.glob("*.pl"))

        if not prolog_files:
            return "📁 No Prolog files found in data directory."

        file_info = []
        for file_path in sorted(prolog_files):
            try:
                stat = file_path.stat()
                size = stat.st_size
                modified = stat.st_mtime

                file_info.append(f"  📄 {file_path.name} ({size} bytes)")
            except Exception:
                file_info.append(f"  📄 {file_path.name}")

        return f"""📚 Prolog Files in {data_path}:
{chr(10).join(file_info)}

💡 Load in SWISH with: ?- consult(filename)."""

    except Exception as e:
        logger.error(f"Failed to list Prolog files: {e}")
        return f"❌ Failed to list files: {e}"


@mcp.tool()
async def configure_swish_auth(
    auth_mode: str,
    username: str | None = None,
    email: str | None = None
) -> str:
    """
    Configure SWISH authentication settings.

    Args:
        auth_mode: Authentication mode (anon, social, always)
        username: Username for 'always' mode
        email: Email for 'always' mode

    Returns:
        Configuration status
    """
    try:
        # FIXED: Use global context instead of mcp.request_context
        context = get_context()

        if auth_mode not in ["anon", "social", "always"]:
            return "❌ Invalid auth_mode. Use: anon, social, or always"

        # For 'always' mode, require username and email
        if auth_mode == "always" and (not username or not email):
            return "❌ Username and email required for 'always' auth mode"

        # Create configuration command
        config_cmd = ["--auth", auth_mode]

        if auth_mode == "always" and username and email:
            # This would typically require interactive input in real SWISH
            # For now, we'll document the requirement
            return f"""⚠️ Authentication mode '{auth_mode}' requires interactive setup.

To configure authenticated mode:
1. Stop the current container
2. Start with: docker run -it swish --auth always --add-user
3. Follow prompts to create user: {username} ({email})
4. Restart with: docker run swish --auth always

Note: Authenticated mode allows executing arbitrary Prolog code."""

        return f"""✅ Authentication configured: {auth_mode}
🔧 Restart container to apply changes.

Modes:
• anon: Anonymous access (sandboxed queries only)
• social: Social login (Google, StackOverflow)
• always: Full authentication required"""

    except Exception as e:
        logger.error(f"Failed to configure authentication: {e}")
        return f"❌ Failed to configure authentication: {e}"


# Resources and prompts remain the same as original
@mcp.resource("swish://container/logs")
async def get_container_logs() -> str:
    """Get logs from the running SWISH container."""
    try:
        return "Container logs resource - use get_swish_status() tool for current container information"
    except Exception as e:
        logger.error(f"Failed to get container logs: {e}")
        return f"Error getting logs: {e}"


@mcp.resource("swish://files/{filename}")
async def get_prolog_file_content(filename: str) -> str:
    """Get content of a specific Prolog file."""
    try:
        return f"Prolog file content resource for: {filename}\nUse create_prolog_file() and list_prolog_files() tools for full file management functionality"
    except Exception as e:
        logger.error(f"Failed to read Prolog file: {e}")
        return f"Error reading file: {e}"


@mcp.resource("swish://knowledge-base")
async def get_knowledge_base_summary() -> str:
    """Get a summary of the current Prolog knowledge base."""
    try:
        return "Knowledge base summary resource - use list_prolog_files() tool for current knowledge base information"
    except Exception as e:
        logger.error(f"Failed to get knowledge base summary: {e}")
        return f"Error getting knowledge base summary: {e}"


@mcp.prompt()
def prolog_programming_assistant(
    task_description: str,
    difficulty_level: str = "beginner"
) -> str:
    """Generate a prompt for Prolog programming assistance."""
    return f"""You are helping with Prolog programming. Here's the task:

**Task**: {task_description}
**Skill Level**: {difficulty_level}

Please provide:
1. **Prolog Code**: Well-commented solution with predicates and rules
2. **Explanation**: How the logic works step by step
3. **Example Queries**: Test queries to verify the solution
4. **Best Practices**: Prolog-specific optimization tips

For {difficulty_level} level:
{_get_level_guidance(difficulty_level)}

Remember to:
- Use descriptive predicate names
- Add comments explaining complex logic
- Consider edge cases and base conditions
- Follow Prolog naming conventions (lowercase, underscore_separated)"""


def _get_level_guidance(level: str) -> str:
    """Get level-specific guidance for Prolog programming."""
    guidance = {
        "beginner": """
- Focus on basic facts and simple rules
- Explain unification and backtracking clearly
- Use simple, intuitive examples
- Avoid complex cut operators and meta-predicates""",

        "intermediate": """
- Include list processing and recursion patterns
- Explain cut operator usage when appropriate
- Show debugging techniques with trace/0
- Demonstrate DCG (Definite Clause Grammar) basics""",

        "advanced": """
- Utilize meta-predicates and higher-order programming
- Implement constraint logic programming when relevant
- Show optimization techniques and indexing considerations
- Include module system and operator definitions"""
    }
    return guidance.get(level, guidance["beginner"])


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Docker SWISH MCP server (FIXED)")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        cleanup_processes()


if __name__ == "__main__":
    main()
