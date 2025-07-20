"""
Docker SWISH MCP Server - Prolog Integration

Automatically manages SWISH container lifecycle and provides seamless Prolog interaction.
Container starts when MCP server starts, stops when MCP server stops.
Main purpose: Enable Claude to use Prolog for logic programming and reasoning.
"""

from __future__ import annotations

import asyncio
import atexit
import logging
import signal
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import aiohttp
from mcp.server.fastmcp import FastMCP

# Import the persistent session manager
from .simple_session import SimplePrologSession

# Try to import docker, but don't fail if not available
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False

# Configure logging to stderr for MCP servers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("docker-swish-mcp")

# Version info
__version__ = "0.3.0"

# Global tracking for cleanup
running_processes: dict[str, Any] = {}
background_tasks: set[asyncio.Task] = set()
global_swish_context: SwishContext | None = None


@dataclass
class SwishContext:
    """Application context for SWISH operations"""
    docker_client: Any = None
    container: Any = None
    container_name: str = "swish-mcp-auto"
    port: int = 3050
    data_dir: Path = Path.cwd() / "swish-data-new"
    swish_base_url: str = "http://localhost:3050"
    docker_available: bool = False
    container_ready: bool = False
    prolog_session: SimplePrologSession | None = None


def cleanup_processes() -> None:
    """Clean up all running processes and background tasks"""
    logger.info("Cleaning up processes and tasks")

    # Cancel background tasks
    for task in background_tasks:
        if not task.done():
            task.cancel()

    # Cleanup persistent Prolog session
    if global_swish_context and global_swish_context.prolog_session:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule cleanup as a task if loop is running
                task = loop.create_task(global_swish_context.prolog_session.cleanup())
                background_tasks.add(task)
            else:
                # Run cleanup directly if no loop is running
                asyncio.run(global_swish_context.prolog_session.cleanup())
            logger.info("Prolog session cleaned up")
        except Exception as e:
            logger.debug(f"Prolog session cleanup: {e}")

    # Stop SWISH container if running
    if global_swish_context and global_swish_context.container:
        try:
            logger.info(f"Stopping SWISH container {global_swish_context.container_name}")
            # First try graceful stop
            global_swish_context.container.stop(timeout=5)
            # Then remove the container
            global_swish_context.container.remove(force=True)
            logger.info("SWISH container stopped and removed successfully")
        except Exception as e:
            logger.debug(f"Container cleanup: {e}")
            # Try to force remove if graceful stop failed
            try:
                if global_swish_context.docker_available and docker:
                    client = docker.from_env()
                    container = client.containers.get(global_swish_context.container_name)
                    container.remove(force=True)
            except Exception as e2:
                logger.debug(f"Force cleanup also failed: {e2}")

    # Clear collections
    running_processes.clear()
    background_tasks.clear()


def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
    cleanup_processes()
    sys.exit(0)


async def start_swish_container(context: SwishContext) -> bool:
    """
    Start SWISH container automatically with proper cleanup and port management.

    Returns:
        True if container started successfully, False otherwise
    """
    try:
        if not context.docker_available:
            logger.warning("Docker not available, cannot start SWISH container")
            return False

        docker_client = context.docker_client

        # Ensure data directory exists (mount the swish-data directly)
        data_path = context.data_dir  # Mount swish-data/ to /data in container
        data_path.mkdir(exist_ok=True)

        # Clean up any existing containers with our name
        try:
            existing = docker_client.containers.get(context.container_name)
            logger.info(f"Found existing container {context.container_name} with status: {existing.status}")

            if existing.status == "running":
                # Check if it's responsive
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{context.swish_base_url}/",
                            timeout=aiohttp.ClientTimeout(total=2)
                        ) as response:
                            if response.status == 200:
                                logger.info("✅ Existing SWISH container is working, reusing it")
                                context.container = existing
                                context.container_ready = True
                                return True
                except Exception:
                    logger.info("Existing container not responsive, will replace it")

                # Stop and remove unresponsive container
                existing.stop(timeout=5)

            # Remove any existing container (stopped or unresponsive)
            existing.remove(force=True)
            logger.info(f"Removed existing container: {context.container_name}")

        except Exception as e:
            logger.debug(f"No existing container found: {e}")

        # Check for port conflicts and clean them up
        try:
            # List all containers using our port
            all_containers = docker_client.containers.list(all=True)
            for container in all_containers:
                if container.ports and any(
                    binding and str(context.port) in str(binding)
                    for bindings in container.ports.values()
                    for binding in (bindings or [])
                ):
                    if container.name != context.container_name:
                        logger.warning(f"Port {context.port} in use by container {container.name}, stopping it")
                        try:
                            if container.status == "running":
                                container.stop(timeout=5)
                            container.remove(force=True)
                        except Exception as e:
                            logger.warning(f"Could not remove conflicting container: {e}")
        except Exception as e:
            logger.debug(f"Port conflict check failed: {e}")

        # Pull latest image
        logger.info("Ensuring SWISH image is available...")
        try:
            docker_client.images.pull("swipl/swish:latest")
        except Exception as e:
            logger.warning(f"Could not pull latest image: {e}")

        # Container configuration for automatic management
        container_config = {
            "image": "swipl/swish:latest",
            "name": context.container_name,
            "ports": {"3050/tcp": context.port},
            "volumes": {str(data_path): {"bind": "/data", "mode": "rw"}},
            "detach": True,
            "remove": False,
            "environment": {},
            "labels": {
                "managed-by": "docker-swish-mcp",
                "mcp-version": __version__,
                "auto-managed": "true"
            },
            "restart_policy": {"Name": "no"}  # Don't auto-restart
        }

        # Start container
        logger.info(f"Starting SWISH container on port {context.port}...")
        container = docker_client.containers.run(**container_config)
        context.container = container

        # Wait for container to be ready
        max_wait = 30
        for _ in range(max_wait):
            try:
                # Refresh container status
                container.reload()
                if container.status != "running":
                    logger.error(f"Container failed to start properly, status: {container.status}")
                    # Get container logs for debugging
                    logs = container.logs().decode('utf-8', errors='ignore')
                    logger.error(f"Container logs: {logs}")
                    return False

                # Check if SWISH is responding
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{context.swish_base_url}/",
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as response:
                        if response.status == 200:
                            context.container_ready = True
                            logger.info(f"✅ SWISH container ready at {context.swish_base_url}")

                            # Initialize persistent Prolog session
                            logger.info("🧠 Initializing persistent Prolog session...")
                            context.prolog_session = SimplePrologSession(context.container_name)
                            session_started = await context.prolog_session.start_session()

                            if session_started:
                                logger.info("✅ Persistent Prolog session ready")
                            else:
                                logger.warning("⚠️ Failed to start persistent Prolog session")
                                logger.warning("Queries will fall back to individual execution mode")

                            return True
            except Exception as e:
                logger.debug(f"Waiting for container readiness: {e}")

            await asyncio.sleep(1)

        logger.error("SWISH container failed to become ready within timeout")
        context.container_ready = False

        # If we get here, try to get logs for debugging
        try:
            logs = container.logs().decode('utf-8', errors='ignore')
            logger.error(f"Container logs: {logs}")
        except Exception:
            pass

        return False

    except Exception as e:
        logger.error(f"Failed to start SWISH container: {e}")
        return False


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[SwishContext]:
    """Manage application lifecycle with automatic SWISH container management"""
    global global_swish_context

    logger.info(f"Initializing Docker SWISH MCP Server v{__version__}")

    context = None  # Ensure context is always defined

    try:
        # Initialize Docker if available
        if DOCKER_AVAILABLE and docker:
            try:
                docker_client = docker.from_env()
                # Test Docker connection
                docker_client.ping()
                docker_available = True
                logger.info("✅ Docker client initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Docker not available: {e}")
                docker_client = None
                docker_available = False
        else:
            logger.warning("⚠️ Docker not available")
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

        # Auto-start SWISH container if Docker is available
        if docker_available:
            logger.info("🚀 Starting SWISH container automatically...")
            success = await start_swish_container(context)
            if success:
                logger.info("✅ SWISH container started successfully")
            else:
                logger.warning("⚠️ Failed to start SWISH container - running in limited mode")
                logger.warning("Container management and Prolog queries will not be available")

        # Set global context
        global_swish_context = context

        logger.info("🧠 MCP Server ready for Prolog interaction")
        if context.container_ready:
            logger.info(f"🌐 SWISH available at: {context.swish_base_url}")

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

        # Cleanup persistent session first
        if context and context.prolog_session:
            try:
                await context.prolog_session.cleanup()
                logger.info("✅ Persistent Prolog session cleaned up")
            except Exception as e:
                logger.debug(f"Session cleanup error: {e}")

        cleanup_processes()
        global_swish_context = None


def refresh_container_reference(context: SwishContext) -> bool:
    """Refresh the container reference in case it was recreated"""
    try:
        if not context.docker_available or not context.docker_client:
            return False

        # Try to get container by name
        try:
            container = context.docker_client.containers.get(context.container_name)
            context.container = container
            context.container_ready = (container.status == "running")
            logger.info(f"Refreshed container reference: {context.container_name} ({container.id[:12]})")
            return True
        except Exception as e:
            logger.warning(f"Could not refresh container reference: {e}")
            context.container = None
            context.container_ready = False
            return False
    except Exception as e:
        logger.error(f"Error refreshing container reference: {e}")
        return False


def get_context() -> SwishContext:
    """Get current context with proper error handling"""
    if global_swish_context is None:
        raise RuntimeError("SWISH context not initialized. Server may not be properly started.")

    # Auto-refresh container reference if needed
    if (global_swish_context.docker_available and
        global_swish_context.container and
        not global_swish_context.container_ready):
        refresh_container_reference(global_swish_context)

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
    description="Seamless Prolog integration with auto-managed SWISH container",
    lifespan=app_lifespan
)

@mcp.tool()
async def execute_prolog_query(
    query: str,
    timeout: int = 30
) -> str:
    """
    Execute a Prolog query against the running SWISH instance with persistent state.

    This is the primary way to interact with Prolog for logic programming,
    reasoning, and knowledge base queries. State persists between queries,
    so consulted files and asserted facts remain available.

    Args:
        query: Prolog query to execute (e.g., "member(X, [1,2,3]).", "?- factorial(5, N).")
        timeout: Timeout in seconds for query execution

    Returns:
        Query results or error message
    """
    try:
        context = get_context()

        if not context.container_ready:
            # Try to refresh container reference and check again
            if context.docker_available:
                refresh_success = refresh_container_reference(context)
                if not refresh_success or not context.container_ready:
                    return "❌ SWISH container is not ready. Please wait a moment and try again or restart the MCP server."
            else:
                return "❌ Docker not available. Cannot execute Prolog queries."

        # Validate query format
        if not query.strip():
            return "❌ Empty query provided"

        # Use persistent session if available
        if context.prolog_session:
            try:
                result = await context.prolog_session.execute_query(query, timeout)

                # Format the response based on result type
                clean_query = query.strip()
                if clean_query.startswith("?-"):
                    clean_query = clean_query[2:].strip()
                if not clean_query.endswith('.'):
                    clean_query = clean_query + '.'

                if result["success"]:
                    if result.get("response_type") == "solutions":
                        solutions = result.get("solutions", [])
                        return f"""✅ Query: {clean_query}
📋 Results:
{chr(10).join(f"  • {solution}" for solution in solutions)}

💡 Total solutions: {len(solutions)} (persistent session)"""

                    elif result.get("response_type") == "simple_success":
                        return f"✅ Query: {clean_query}\n📋 Result: true (query succeeded)"

                    else:
                        return f"✅ Query: {clean_query}\n📋 Result: Query completed successfully"

                elif result.get("response_type") == "failure":
                    return f"❌ Query: {clean_query}\n📋 Result: false (no solutions found)"

                else:
                    error_msg = result.get("error", "Unknown error")
                    return f"❌ Query: {clean_query}\n📋 Error: {error_msg}"

            except Exception as session_error:
                logger.warning(f"Persistent session failed: {session_error}")
                logger.info("Falling back to direct execution mode")
                # Fall through to backup execution mode below

        # Backup execution mode (original implementation)
        logger.info("Using direct container execution as fallback for Prolog query")

        # Clean up query - remove leading ?- if present, ensure ends with period
        clean_query = query.strip()
        if clean_query.startswith("?-"):
            clean_query = clean_query[2:].strip()
        if not clean_query.endswith('.'):
            clean_query = clean_query + '.'

        # Execute query via direct container execution
        try:
            # Build the command to execute in the container
            # For queries with variables, we need to format output specially
            if any(c.isupper() for c in clean_query):  # Has variables
                prolog_cmd = f"""
                (   {clean_query[:-1]},
                    term_variables({clean_query[:-1]}, Vars),
                    copy_term({clean_query[:-1]}, Term),
                    numbervars(Term, 0, _),
                    writeq(solution(Term)), nl,
                    fail
                ;   write('no_more_solutions'), nl
                ), halt.
                """
            else:  # No variables, just test success/failure
                prolog_cmd = f"""
                (   {clean_query[:-1]} ->
                    write('success'), nl
                ;   write('failure'), nl
                ), halt.
                """

            # Execute the command in the container
            cmd = [
                "docker", "exec", context.container_name,
                "swipl", "-g", prolog_cmd, "-t", "halt"
            ]

            # Run the command asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            # Process the output
            output = stdout.decode('utf-8').strip()
            error_output = stderr.decode('utf-8').strip()

            if process.returncode != 0:
                if error_output:
                    return f"❌ Prolog Error in query '{clean_query}': {error_output}"
                else:
                    return f"❌ Query execution failed: {clean_query}"

            if not output:
                return f"❌ Query: {clean_query}\n📋 Result: No output (query may have failed)"

            # Parse the results
            lines = output.split('\n')
            results = []

            for line in lines:
                line = line.strip()
                if line == 'no_more_solutions':
                    break
                elif line == 'success':
                    return f"✅ Query: {clean_query}\n📋 Result: true (query succeeded)"
                elif line == 'failure':
                    return f"❌ Query: {clean_query}\n📋 Result: false (no solutions found)"
                elif line.startswith('solution('):
                    # Extract the solution
                    solution = line[9:-1]  # Remove 'solution(' and ')'
                    results.append(solution)
                elif line and line != 'no_more_solutions':
                    results.append(line)

            if results:
                return f"""✅ Query: {clean_query}
📋 Results:
{chr(10).join(f"  • {result}" for result in results)}

💡 Total solutions: {len(results)} (direct execution - no persistence)"""
            else:
                return f"✅ Query: {clean_query}\n📋 Result: Query completed successfully (direct execution)"

        except asyncio.TimeoutError:
            return f"⏱️ Query timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Direct execution failed: {e}")
            return f"❌ Failed to execute query via both persistent session and direct execution: {e}"

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

    Use this to create logic programs, facts, and rules that can be
    consulted and used in Prolog queries.

    Args:
        filename: Name of the .pl file (without extension)
        content: Prolog code content (facts, rules, predicates)
        overwrite: Whether to overwrite existing file

    Returns:
        Status message with instructions on how to use the file
    """
    try:
        context = get_context()

        # Ensure filename has .pl extension
        if not filename.endswith('.pl'):
            filename = f"{filename}.pl"

        # Create file path in swish-data directory (mounted as /data in container)
        file_path = context.data_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists
        if file_path.exists() and not overwrite:
            return f"❌ File '{filename}' already exists. Use overwrite=True to replace."

        # Write Prolog content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created Prolog file: {file_path}")

        # Get the basename without extension for consulting
        base_name = filename[:-3] if filename.endswith('.pl') else filename

        return f"""✅ Created Prolog file: {filename}
📁 Path: {file_path}
📝 Size: {len(content)} characters
🔄 To use this knowledge base, run: ?- consult({base_name}).

💡 Example queries after consulting:
   - List all predicates: ?- current_predicate(F/A).
   - Get help: ?- help({base_name}).
"""

    except Exception as e:
        logger.error(f"Failed to create Prolog file: {e}")
        return f"❌ Failed to create file: {e}"


@mcp.tool()
async def list_prolog_files() -> str:
    """
    List all Prolog files in the SWISH data directory.

    Shows available knowledge bases that can be consulted.

    Returns:
        List of available Prolog files with sizes and usage instructions
    """
    try:
        context = get_context()
        data_path = context.data_dir

        if not data_path.exists():
            return "📁 No data directory found. Create some Prolog files first with create_prolog_file()."

        # Find all .pl files
        prolog_files = list(data_path.glob("*.pl"))

        if not prolog_files:
            return """📁 No Prolog files found in data directory.

💡 Create your first knowledge base:
   create_prolog_file("example", "
   % Facts
   parent(tom, bob).
   parent(bob, ann).

   % Rules
   grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
   ")"""

        file_info = []
        for file_path in sorted(prolog_files):
            try:
                stat = file_path.stat()
                size = stat.st_size
                base_name = file_path.stem

                file_info.append(f"  📄 {file_path.name} ({size} bytes)")
                file_info.append(f"      💡 Load with: ?- consult({base_name}).")
            except Exception:
                file_info.append(f"  📄 {file_path.name}")

        return f"""📚 Prolog Knowledge Bases in {data_path}:
{chr(10).join(file_info)}

🔄 After loading files, you can:
   - Query facts: ?- parent(tom, bob).
   - Test rules: ?- grandparent(tom, ann).
   - List predicates: ?- current_predicate(F/A).
"""

    except Exception as e:
        logger.error(f"Failed to list Prolog files: {e}")
        return f"❌ Failed to list files: {e}"


@mcp.tool()
async def get_swish_status() -> str:
    """
    Get the current status of the SWISH container and Prolog environment.

    Useful for troubleshooting and checking if the Prolog environment is ready.

    Returns:
        Detailed status information about the SWISH container and service
    """
    try:
        context = get_context()

        if not context.docker_available:
            return """⚠️ Docker is not available

The MCP server is running but cannot manage containers.
Please ensure Docker Desktop is running and accessible."""

        if not context.container:
            # Try to refresh container reference first
            refresh_success = refresh_container_reference(context)
            if not refresh_success:
                return """❌ No SWISH container found

Container failed to start during initialization or was removed.
Try restarting the MCP server or check Docker status."""

        try:
            # Refresh container status - handle stale references
            try:
                context.container.reload()
            except Exception as reload_error:
                logger.warning(f"Container reload failed, trying to refresh reference: {reload_error}")
                if not refresh_container_reference(context):
                    return f"❌ Container reference is stale and could not be refreshed: {reload_error}"

            status = context.container.status

            # Check SWISH accessibility
            swish_accessible = False
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{context.swish_base_url}/",
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as response:
                        swish_accessible = response.status == 200
            except Exception:
                pass

            # Get basic container info
            created = context.container.attrs.get('Created', 'Unknown')

            # Get persistent session status
            session_status = ""
            if context.prolog_session:
                session_info = context.prolog_session.get_status()
                session_status = f"""
🧠 Persistent Session: {'✅ Active' if session_info['active'] else '❌ Inactive'}
📊 Queries Executed: {session_info['query_count']}
📚 Consulted Files: {', '.join(session_info['consulted_files']) if session_info['consulted_files'] else 'None'}"""
            else:
                session_status = "\n🧠 Persistent Session: ⚠️ Not initialized"

            return f"""📊 SWISH Prolog Environment Status

🐳 Container: {context.container.name} ({context.container.id[:12]})
📊 Status: {status.upper()}
🌐 URL: {context.swish_base_url}
🚀 Service: {'✅ Ready for Prolog queries' if swish_accessible else '⚠️ Starting up...'}
📅 Started: {created[:19] if 'T' in created else created}
📁 Data: {context.data_dir}{session_status}

💡 {'Ready to execute Prolog queries with persistent state!' if swish_accessible and context.prolog_session and context.prolog_session.get_status()['active'] else 'Container starting or session initializing, please wait...'}

🧠 Available operations:
   - execute_prolog_query("member(X, [1,2,3]).")
   - create_prolog_file("my_kb", "fact(a). rule(X) :- fact(X).")
   - list_prolog_files()
"""

        except Exception as e:
            return f"❌ Error checking container status: {e}"

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return f"❌ Failed to get status: {e}"


@mcp.tool()
async def load_knowledge_base(filename: str) -> str:
    """
    Load (consult) a Prolog knowledge base file into the SWISH session.

    This makes the facts and rules in the file available for queries.

    Args:
        filename: Name of the .pl file to load (with or without extension)

    Returns:
        Status of the loading operation
    """
    try:
        context = get_context()

        if not context.container_ready:
            return "❌ SWISH container is not ready. Please wait a moment and try again."

        # Ensure filename has .pl extension for file checking
        if not filename.endswith('.pl'):
            check_filename = f"{filename}.pl"
            consult_name = filename
        else:
            check_filename = filename
            consult_name = filename[:-3]  # Remove .pl for consulting

        # Check if file exists
        file_path = context.data_dir / check_filename
        if not file_path.exists():
            return f"❌ File '{check_filename}' not found. Use list_prolog_files() to see available files."

        # Load the knowledge base using consult
        consult_query = f"consult({consult_name})."
        result = await execute_prolog_query(consult_query)

        if "✅" in result:
            # Track the consulted file in the persistent session
            # Note: Simplified session doesn't track consulted files
            # if context.prolog_session:
            #     context.prolog_session.track_consult(consult_name)

            return f"""✅ Knowledge base '{check_filename}' loaded successfully!

📚 The facts and rules from {check_filename} are now available.
💡 You can now query them directly, for example:
   - List all facts: ?- current_predicate(F/A).
   - Query specific facts from your knowledge base

🔍 File loaded from: {file_path}
"""
        else:
            return f"⚠️ There may have been an issue loading the file:\n{result}"

    except Exception as e:
        logger.error(f"Failed to load knowledge base: {e}")
        return f"❌ Failed to load knowledge base: {e}"


@mcp.tool()
async def restart_prolog_session() -> str:
    """
    Restart the persistent Prolog session.

    This can be useful if the session becomes unresponsive or if you want
    to start fresh while preserving consulted knowledge bases.

    Returns:
        Status of the restart operation
    """
    try:
        context = get_context()

        if not context.container_ready:
            return "❌ SWISH container is not ready. Cannot restart Prolog session."

        if not context.prolog_session:
            logger.info("No existing session, creating new persistent session")
            context.prolog_session = SimplePrologSession(context.container_name)
            success = await context.prolog_session.start_session()

            if success:
                return "✅ New persistent Prolog session started successfully!"
            else:
                return "❌ Failed to start new persistent Prolog session"

        # Restart existing session
        logger.info("Restarting persistent Prolog session")
        success = await context.prolog_session.restart_session()

        if success:
            session_info = context.prolog_session.get_status()
            consulted_files = session_info.get('consulted_files', [])

            restart_msg = "✅ Persistent Prolog session restarted successfully!"
            if consulted_files:
                restart_msg += f"\n📚 Re-consulted files: {', '.join(consulted_files)}"

            return restart_msg
        else:
            return "❌ Failed to restart persistent Prolog session"

    except Exception as e:
        logger.error(f"Failed to restart Prolog session: {e}")
        return f"❌ Failed to restart session: {e}"


# AI assistance prompts for Prolog programming
@mcp.prompt()
def prolog_programming_assistant(
    task_description: str,
    difficulty_level: str = "beginner"
) -> str:
    """Generate a prompt for Prolog programming assistance tailored to specific tasks."""
    return f"""You are an expert Prolog programming assistant helping with logic programming tasks.

**Task**: {task_description}
**Skill Level**: {difficulty_level}

Please provide:
1. **Prolog Code**: Well-commented solution with predicates and rules
2. **Step-by-Step Explanation**: How the logic works and why
3. **Example Queries**: Test queries to verify the solution works
4. **Usage Instructions**: How to load and use the code in SWISH

For {difficulty_level} level, focus on:
{_get_level_guidance(difficulty_level)}

**Prolog Best Practices to Follow:**
- Use descriptive predicate names (snake_case)
- Add comments explaining complex logic
- Handle base cases and recursive cases clearly
- Consider cut operators (!) only when necessary
- Test edge cases and boundary conditions

**Remember**: The user has access to a SWISH environment where they can:
- Create files with create_prolog_file("name", "content")
- Load knowledge bases with load_knowledge_base("name")
- Execute queries with execute_prolog_query("query")
- List available files with list_prolog_files()

Make your solution practical and ready to use in their environment.
"""


@mcp.prompt()
def logic_rule_creation(
    domain: str,
    relationships: str
) -> str:
    """Generate a prompt for creating domain-specific logic rules in Prolog."""
    return f"""You are helping create a Prolog knowledge base for the domain: {domain}

**Domain**: {domain}
**Relationships to model**: {relationships}

Please create a comprehensive Prolog knowledge base that includes:

1. **Facts**: Basic facts about entities in this domain
2. **Rules**: Logical relationships and inference rules
3. **Queries**: Example queries to demonstrate the knowledge base
4. **Documentation**: Comments explaining the logic

**Structure your response as:**
```prolog
% Knowledge Base for {domain}
% Created for SWISH MCP environment

% ============================================
% FACTS (Basic information)
% ============================================

% [Your facts here]

% ============================================
% RULES (Logical relationships)
% ============================================

% [Your rules here]

% ============================================
% UTILITY PREDICATES (Helper functions)
% ============================================

% [Helper predicates here]
```

**Also provide example queries** that demonstrate:
- Simple fact retrieval
- Rule-based inference
- Complex reasoning scenarios

**Make it practical** - the user can immediately:
1. Save this as a .pl file using create_prolog_file()
2. Load it with load_knowledge_base()
3. Test it with execute_prolog_query()

Focus on clarity, correctness, and educational value.
"""


def _get_level_guidance(level: str) -> str:
    """Get level-specific guidance for Prolog programming."""
    guidance = {
        "beginner": """
- Simple facts and basic rules
- Clear variable names and simple unification
- Avoid complex operators like cut (!)
- Focus on basic list operations and recursion
- Provide step-by-step reasoning explanations""",

        "intermediate": """
- List processing and recursive patterns
- Appropriate use of cut operator when needed
- Debugging techniques and trace usage
- Basic DCG (Definite Clause Grammar) concepts
- Efficiency considerations and optimization""",

        "advanced": """
- Meta-predicates and higher-order programming
- Constraint logic programming techniques
- Advanced optimization and indexing
- Module system and operator definitions
- Complex data structure manipulation"""
    }
    return guidance.get(level, guidance["beginner"])


# Resources for additional information
@mcp.resource("swish://container/info")
async def get_container_info() -> str:
    """Get current SWISH container information."""
    try:
        context = get_context()

        if not context.container:
            return "No SWISH container currently running"

        return f"""SWISH Container Information:
Name: {context.container_name}
Status: {context.container.status if context.container else 'Not running'}
URL: {context.swish_base_url}
Data Directory: {context.data_dir}
Ready: {context.container_ready}

This container is automatically managed by the MCP server.
"""
    except Exception as e:
        return f"Error getting container info: {e}"


@mcp.resource("swish://files/list")
async def get_files_list() -> str:
    """Get list of available Prolog files as a resource."""
    try:
        context = get_context()
        data_path = context.data_dir

        if not data_path.exists():
            return "No Prolog files directory found"

        prolog_files = list(data_path.glob("*.pl"))

        if not prolog_files:
            return "No Prolog files found"

        file_list = []
        for file_path in sorted(prolog_files):
            try:
                stat = file_path.stat()
                size = stat.st_size
                file_list.append(f"{file_path.name} ({size} bytes)")
            except Exception:
                file_list.append(file_path.name)

        return f"""Available Prolog Files:
{chr(10).join(file_list)}

Use load_knowledge_base() to load any of these files.
"""
    except Exception as e:
        return f"Error listing files: {e}"


# Main entry point
def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info("=" * 60)
        logger.info(f"Docker SWISH MCP Server v{__version__}")
        logger.info("Prolog Integration Server")
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
