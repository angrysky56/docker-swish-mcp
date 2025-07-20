"""
Persistent Prolog Session Management for Docker SWISH MCP

This module provides a persistent Prolog session that maintains state between queries,
solving the issue where consulted knowledge bases would disappear between separate queries.
"""

import asyncio
import logging
import re
import uuid
from typing import Any

logger = logging.getLogger("docker-swish-mcp.session")


class PersistentPrologSession:
    """
    Manages a persistent SWI-Prolog session within a Docker container.

    This maintains state between queries, allowing consulted files and asserted
    facts to persist across multiple execute_prolog_query() calls.
    """

    def __init__(self, container_name: str):
        self.container_name = container_name
        self.process: asyncio.subprocess.Process | None = None
        self.session_lock = asyncio.Lock()
        self.session_active = False
        self.query_counter = 0
        self.consulted_files: set[str] = set()

    async def start_session(self) -> bool:
        """
        Start a persistent SWI-Prolog session in the container.

        Returns:
            True if session started successfully, False otherwise
        """
        async with self.session_lock:
            try:
                if self.session_active and self.process and self.process.returncode is None:
                    logger.info("Prolog session already active")
                    return True

                logger.info(f"Starting persistent Prolog session in container {self.container_name}")

                # Start interactive SWI-Prolog process in the container
                cmd = [
                    "docker", "exec", "-i", self.container_name,
                    "swipl", "-q", "--traditional"  # Quiet mode, traditional syntax
                ]

                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                # Wait a moment for process to initialize
                await asyncio.sleep(0.5)

                # Check if process started successfully
                if self.process.returncode is not None:
                    stderr_output = b""
                    if self.process.stderr is not None:
                        stderr_output = await self.process.stderr.read()
                    logger.error(f"Prolog process failed to start: {stderr_output.decode()}")
                    return False

                # Test the session with a simple query
                test_result = await self._execute_raw_query("true", timeout=5)
                if test_result.get("success"):
                    self.session_active = True
                    logger.info("✅ Persistent Prolog session started successfully")
                    return True
                else:
                    logger.error("Session test query failed")
                    await self._cleanup_process()
                    return False

            except Exception as e:
                logger.error(f"Failed to start Prolog session: {e}")
                await self._cleanup_process()
                return False

    async def execute_query(self, query: str, timeout: int = 30) -> dict[str, Any]:
        """
        Execute a Prolog query in the persistent session.

        Args:
            query: Prolog query to execute
            timeout: Maximum time to wait for response

        Returns:
            Dictionary with query results and metadata
        """
        async with self.session_lock:
            # Ensure session is active
            if not await self._ensure_session_active():
                return {"success": False, "error": "Failed to start/maintain Prolog session"}

            # Clean up the query
            clean_query = query.strip()
            if clean_query.startswith("?-"):
                clean_query = clean_query[2:].strip()
            if not clean_query.endswith('.'):
                clean_query = clean_query + '.'

            # Execute the query
            return await self._execute_raw_query(clean_query, timeout)

    async def _execute_raw_query(self, query: str, timeout: int) -> dict[str, Any]:
        """Execute a raw Prolog query and parse the response."""
        try:
            if not self.process or self.process.returncode is not None:
                return {"success": False, "error": "Prolog process not active"}

            self.query_counter += 1
            query_id = f"Q{self.query_counter}"

            # Create a unique response terminator
            terminator = f"DONE_{query_id}_{uuid.uuid4().hex[:8]}"

            # Build the query with output formatting
            if self._has_variables(query):
                # Query with variables - collect all solutions
                formatted_query = f"""
(   forall(
        {query[:-1]},
        (   term_variables({query[:-1]}, Vars),
            copy_term({query[:-1]}, Term),
            numbervars(Term, 0, _),
            format('SOLUTION: ~w~n', [Term])
        )
    ),
    write('SUCCESS\\n')
;   write('FAILURE\\n')
),
write('{terminator}\\n'),
flush_output.
"""
            else:
                # Simple query - just test success/failure
                formatted_query = f"""
(   {query[:-1]} ->
    write('SUCCESS\\n')
;   write('FAILURE\\n')
),
write('{terminator}\\n'),
flush_output.
"""

            # Send query to Prolog process
            if self.process.stdin:
                self.process.stdin.write(formatted_query.encode('utf-8'))
                await self.process.stdin.drain()

            # Read response with timeout
            response_lines = []
            success = False
            solutions = []

            try:
                while True:
                    if self.process.stdout is None:
                        raise RuntimeError("Prolog process stdout is not available")
                    line_bytes = await asyncio.wait_for(
                        self.process.stdout.readline(),
                        timeout=timeout
                    )

                    if not line_bytes:
                        break

                    line = line_bytes.decode('utf-8').strip()
                    response_lines.append(line)

                    # Check for termination
                    if line == terminator:
                        break
                    elif line == "SUCCESS":
                        success = True
                    elif line == "FAILURE":
                        success = False
                    elif line.startswith("SOLUTION: "):
                        solution = line[10:]  # Remove "SOLUTION: " prefix
                        solutions.append(solution)
                    elif line.startswith("ERROR:"):
                        return {
                            "success": False,
                            "error": line,
                            "query": query,
                            "response_lines": response_lines
                        }

                # Process results
                if solutions:
                    return {
                        "success": True,
                        "solutions": solutions,
                        "query": query,
                        "response_type": "solutions"
                    }
                elif success:
                    return {
                        "success": True,
                        "query": query,
                        "response_type": "simple_success"
                    }
                else:
                    return {
                        "success": False,
                        "query": query,
                        "response_type": "failure"
                    }

            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "error": f"Query timed out after {timeout} seconds",
                    "query": query
                }

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    async def restart_session(self) -> bool:
        """
        Restart the Prolog session, preserving consulted files.

        Returns:
            True if restart successful, False otherwise
        """
        logger.info("Restarting Prolog session...")

        # Save currently consulted files
        consulted_backup = self.consulted_files.copy()

        # Cleanup old session
        await self._cleanup_process()

        # Start new session
        if await self.start_session():
            # Re-consult previously loaded files
            for filename in consulted_backup:
                logger.info(f"Re-consulting {filename}")
                result = await self._execute_raw_query(f"consult({filename}).", timeout=10)
                if result.get("success"):
                    self.consulted_files.add(filename)
                else:
                    logger.warning(f"Failed to re-consult {filename}")

            return True
        else:
            return False

    async def _ensure_session_active(self) -> bool:
        """Ensure the Prolog session is active, starting/restarting if needed."""
        if not self.session_active or not self.process or self.process.returncode is not None:
            return await self.start_session()
        return True

    async def cleanup(self) -> None:
        """Clean up the Prolog session."""
        async with self.session_lock:
            await self._cleanup_process()

    async def _cleanup_process(self) -> None:
        """Internal cleanup of the subprocess."""
        self.session_active = False

        if self.process:
            try:
                if self.process.returncode is None:
                    # Try graceful shutdown
                    if self.process.stdin:
                        self.process.stdin.write(b"halt.\n")
                        await self.process.stdin.drain()
                        self.process.stdin.close()

                    # Wait briefly for graceful shutdown
                    try:
                        await asyncio.wait_for(self.process.wait(), timeout=2)
                    except asyncio.TimeoutError:
                        # Force terminate if graceful shutdown failed
                        self.process.terminate()
                        try:
                            await asyncio.wait_for(self.process.wait(), timeout=2)
                        except asyncio.TimeoutError:
                            self.process.kill()
                            await self.process.wait()

            except Exception as e:
                logger.debug(f"Process cleanup error: {e}")
            finally:
                self.process = None

    def _has_variables(self, query: str) -> bool:
        """Check if a query contains variables (uppercase letters)."""
        # Simple heuristic: check for uppercase letters that could be variables
        # This isn't perfect but works for most common cases
        return bool(re.search(r'\b[A-Z][a-zA-Z0-9_]*\b', query))

    def track_consult(self, filename: str) -> None:
        """Track a consulted file for session restart purposes."""
        self.consulted_files.add(filename)

    def get_status(self) -> dict[str, Any]:
        """Get current session status information."""
        return {
            "active": self.session_active,
            "process_alive": self.process is not None and self.process.returncode is None,
            "query_count": self.query_counter,
            "consulted_files": list(self.consulted_files),
            "container": self.container_name
        }
