"""
Simplified Persistent Prolog Session for Docker SWISH MCP

This version focuses on core functionality with robust communication.
"""

import asyncio
import logging
import re
from typing import Any

logger = logging.getLogger("docker-swish-mcp.session")


class SimplePrologSession:
    """
    A simplified persistent SWI-Prolog session that maintains state between queries.
    """

    def __init__(self, container_name: str):
        self.container_name = container_name
        self.process: asyncio.subprocess.Process | None = None
        self.session_lock = asyncio.Lock()
        self.session_active = False
        self.query_counter = 0

    async def start_session(self) -> bool:
        """Start the persistent Prolog session."""
        async with self.session_lock:
            try:
                if self.session_active and self.process and self.process.returncode is None:
                    return True

                logger.info(f"Starting simplified Prolog session in {self.container_name}")

                # Start interactive SWI-Prolog
                cmd = ["docker", "exec", "-i", self.container_name, "swipl", "-q"]

                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                # Wait for startup
                await asyncio.sleep(1.5)

                if self.process.returncode is not None:
                    logger.error("Process failed to start")
                    return False

                # Simple test
                success = await self._test_session()
                if success:
                    self.session_active = True
                    logger.info("✅ Simplified session started")
                    return True
                else:
                    logger.error("Session test failed")
                    await self._internal_cleanup()
                    return False

            except Exception as e:
                logger.error(f"Session start failed: {e}")
                await self._cleanup()
                return False
    async def _internal_cleanup(self) -> None:
        """Clean up resources for the Prolog session."""
        try:
            if self.process:
                self.process.terminate()
                await self.process.wait()
                self.process = None
                self.session_active = False
        except Exception as e:
            import logging
            logger = logging.getLogger("docker-swish-mcp")
            logger.debug(f"Error during session cleanup: {e}")

    async def _test_session(self) -> bool:
        """Test if the session is working with a simple query."""
        try:
            if not self.process or not self.process.stdin:
                return False

            # Send simple test
            test_input = "write('SESSION_OK'), nl.\n"
            self.process.stdin.write(test_input.encode())
            await self.process.stdin.drain()

            # Read response with timeout
            try:
                if self.process.stdout is None:
                    logger.error("Process stdout is None")
                    return False
                response = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=3.0
                )
                result = response.decode().strip()
                return "SESSION_OK" in result
            except asyncio.TimeoutError:
                logger.error("Session test timeout")
                return False

        except Exception as e:
            logger.error(f"Session test error: {e}")
            return False

    async def execute_query(self, query: str, timeout: int = 30) -> dict[str, Any]:
        """Execute a query in the persistent session."""
        async with self.session_lock:
            if not await self._ensure_active():
                return {"success": False, "error": "Session not available"}

            return await self._run_query(query, timeout)

    async def _ensure_active(self) -> bool:
        """Ensure session is active."""
        if not self.session_active or not self.process or self.process.returncode is not None:
            return await self.start_session()
        return True

    async def _run_query(self, query: str, timeout: int) -> dict[str, Any]:
        """Execute query with simplified protocol."""
        try:
            # Clean query
            clean_query = query.strip()
            if clean_query.startswith("?-"):
                clean_query = clean_query[2:].strip()
            if not clean_query.endswith('.'):
                clean_query = clean_query + '.'

            self.query_counter += 1

            # Determine if query has variables
            has_vars = bool(re.search(r'\b[A-Z][a-zA-Z0-9_]*\b', clean_query))

            if has_vars:
                # For variable queries, use findall to collect solutions
                query_cmd = f"findall(X, {clean_query[:-1]}, Solutions), (Solutions = [] -> write('FALSE') ; (write('SOLUTIONS:'), write(Solutions))), nl.\n"
            else:
                # For simple queries, just test true/false
                query_cmd = f"({clean_query[:-1]} -> write('TRUE') ; write('FALSE')), nl.\n"

            # Send query
            if self.process and self.process.stdin:
                self.process.stdin.write(query_cmd.encode())
                await self.process.stdin.drain()

            # Read response
            try:
                if self.process is None or self.process.stdout is None:
                    return {
                        "success": False,
                        "error": "Process or its stdout is None",
                        "query": clean_query
                    }
                response_line = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=timeout
                )

                response = response_line.decode().strip()

                # Parse response
                if has_vars and response.startswith('SOLUTIONS:'):
                    solutions_str = response[10:]  # Remove 'SOLUTIONS:' prefix
                    # Parse the list - this is simplified parsing
                    if solutions_str.startswith('[') and solutions_str.endswith(']'):
                        # Extract solutions from list format
                        solutions_content = solutions_str[1:-1]  # Remove brackets
                        if solutions_content.strip():
                            solutions = [s.strip() for s in solutions_content.split(',')]
                            return {
                                "success": True,
                                "solutions": solutions,
                                "query": clean_query,
                                "response_type": "solutions"
                            }
                        else:
                            return {
                                "success": False,
                                "query": clean_query,
                                "response_type": "failure"
                            }
                    else:
                        return {
                            "success": True,
                            "solutions": [solutions_str],
                            "query": clean_query,
                            "response_type": "solutions"
                        }
                elif response == "TRUE" or "true" in response.lower():
                    return {
                        "success": True,
                        "query": clean_query,
                        "response_type": "simple_success"
                    }
                elif response == "FALSE" or "false" in response.lower():
                    return {
                        "success": False,
                        "query": clean_query,
                        "response_type": "failure"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Unexpected response: {response}",
                        "query": clean_query
                    }

            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "error": f"Query timed out after {timeout} seconds",
                    "query": clean_query
                }

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    async def cleanup(self) -> None:
        """Cleanup the session."""
        async with self.session_lock:
            await self._cleanup()

    async def _cleanup(self) -> None:
        """Internal cleanup."""
        self.session_active = False

        if self.process:
            try:
                if self.process.returncode is None:
                    if self.process.stdin:
                        self.process.stdin.write(b"halt.\n")
                        await self.process.stdin.drain()
                        self.process.stdin.close()

                    try:
                        await asyncio.wait_for(self.process.wait(), timeout=2)
                    except asyncio.TimeoutError:
                        self.process.terminate()
                        try:
                            await asyncio.wait_for(self.process.wait(), timeout=2)
                        except asyncio.TimeoutError:
                            self.process.kill()

            except Exception as e:
                logger.debug(f"Cleanup error: {e}")
            finally:
                self.process = None

    def get_status(self) -> dict[str, Any]:
        """Get session status."""
        return {
            "active": self.session_active,
            "process_alive": self.process is not None and self.process.returncode is None,
            "query_count": self.query_counter,
            "container": self.container_name
        }
