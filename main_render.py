#!/usr/bin/env python
"""
Fixed MCP server for Render deployment
"""
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.responses import Response, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
import os
import sys
import argparse
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

load_dotenv()

# Version identifier
VERSION = "2.5.0-middleware-fix"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Starting mem0-mcp server version {VERSION}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Script path: {__file__}")

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("mem0-mcp")

# Initialize mem0 client and set default user
mem0_client = MemoryClient()
DEFAULT_USER_ID = "cursor_mcp"

def retry_operation(func, max_retries=3, retry_delay=1.0):
    """
    Retry an operation with exponential backoff
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Operation failed after {max_retries} attempts: {str(e)}")
    
    raise last_exception

# Basic Tools (always enabled)
@mcp.tool(
    description="""Add new information to your personal memory. This tool stores any important information 
    about yourself, your preferences, knowledge, or anything you want me to remember."""
)
async def add_memory(text: str) -> str:
    """Add new information to personal memory."""
    try:
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1")
        return f"Successfully added to memory: {text}"
    except Exception as e:
        return f"Error adding to memory: {str(e)}"

@mcp.tool(
    description="""Retrieve all stored memories for the user. Returns a comprehensive list of all stored 
    information including personal details, preferences, knowledge, and more."""
)
async def get_all_memories() -> str:
    """Get all stored memories for the user."""
    try:
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=50)
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error getting memories: {str(e)}"

@mcp.tool(
    description="""Search through stored memories using semantic search. This tool should be called 
    for EVERY user query to find relevant information and context."""
)
async def search_memories(query: str) -> str:
    """Search memories using semantic search."""
    try:
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, output_format="v1.1")
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

# Advanced tools
@mcp.tool(
    description="Update an existing memory with new content"
)
def update_memory(memory_id: str, new_content: str) -> str:
    """Update an existing memory"""
    try:
        def _update():
            return mem0_client.update(memory_id, new_content, user_id=DEFAULT_USER_ID)
        
        retry_operation(_update)
        return f"Successfully updated memory {memory_id}"
    except Exception as e:
        return f"Error updating memory: {str(e)}"

@mcp.tool(
    description="Delete a specific memory by ID"
)
def delete_memory(memory_id: str) -> str:
    """Delete a memory"""
    try:
        def _delete():
            return mem0_client.delete(memory_id, user_id=DEFAULT_USER_ID)
        
        retry_operation(_delete)
        return f"Successfully deleted memory {memory_id}"
    except Exception as e:
        return f"Error deleting memory: {str(e)}"

@mcp.tool(
    description="Get statistics about stored memories"
)
def get_memory_stats() -> str:
    """Get memory statistics"""
    try:
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=100)
        
        stats = {
            "total_memories": len(memories["results"]),
            "memory_types": {},
            "recent_count": 0
        }
        
        # Analyze memory types
        for memory in memories["results"]:
            content = memory.get("memory", "").lower()
            if "personal" in content or "name" in content:
                stats["memory_types"]["personal"] = stats["memory_types"].get("personal", 0) + 1
            elif "work" in content or "job" in content:
                stats["memory_types"]["work"] = stats["memory_types"].get("work", 0) + 1
            else:
                stats["memory_types"]["other"] = stats["memory_types"].get("other", 0) + 1
        
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error getting stats: {str(e)}"

@mcp.tool(
    description="Check if there are relevant memories before answering questions"
)
def check_relevant_memories(topic: str) -> str:
    """Quick check for relevant memories about a topic"""
    try:
        def _search():
            return mem0_client.search(topic, user_id=DEFAULT_USER_ID, limit=5, output_format="v1.1")
        
        memories = retry_operation(_search)
        
        if not memories["results"]:
            return "No relevant memories found for this topic."
        
        summary = f"Found {len(memories['results'])} relevant memories:\n"
        for i, memory in enumerate(memories["results"], 1):
            content = memory.get("memory", "")
            if len(content) > 100:
                content = content[:97] + "..."
            summary += f"{i}. {content}\n"
        
        return summary
    except Exception as e:
        return f"Error checking memories: {str(e)}"

# Create health check endpoint
async def health_check(request: Request):
    return Response(
        content=json.dumps({
            "status": "healthy", 
            "service": "mem0-mcp", 
            "version": VERSION,
            "timestamp": datetime.now().isoformat()
        }),
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Debug endpoint to check SSE transport state
async def debug_sse(request: Request):
    debug_info = {
        "version": VERSION,
        "sse_endpoint": "/sse",
        "messages_endpoint": "/messages/",
        "instructions": {
            "1": "Connect to /sse using EventSource or SSE client",
            "2": "Server will send 'endpoint' event with session URL",
            "3": "Use that URL for subsequent POST requests to /messages/"
        },
        "timestamp": datetime.now().isoformat()
    }
    return JSONResponse(
        content=debug_info,
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Endpoint to handle stale sessions and guide reconnection
async def handle_session_error(request: Request):
    """Return guidance for clients with invalid sessions"""
    return JSONResponse(
        content={
            "error": "session_not_found",
            "message": "Session has expired or was not found. Please reconnect to /sse endpoint.",
            "reconnect_url": "/sse",
            "instructions": [
                "1. Close any existing SSE connections",
                "2. Connect to /sse endpoint",
                "3. Wait for 'endpoint' event with new session URL",
                "4. Use the new session URL for subsequent requests"
            ]
        },
        status_code=404,
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Note: BaseHTTPMiddleware is incompatible with SSE streaming responses
# We'll handle errors within the route handlers instead

# Middleware to intercept stale sessions
class StaleSessionMiddleware:
    """Middleware to intercept and handle stale session requests"""
    KNOWN_STALE_SESSION = "467db479-421a-41d2-9ff4-a7ad29678bb6"
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        """ASGI middleware to intercept stale sessions"""
        if scope["type"] == "http" and scope["path"].startswith("/messages/"):
            # Parse query string
            query_string = scope.get("query_string", b"").decode()
            
            # Check if this is the stale session
            if f"session_id={self.KNOWN_STALE_SESSION}" in query_string:
                logger.warning(f"StaleSessionMiddleware: Intercepted stale session request")
                
                # Send 410 Gone response
                await send({
                    "type": "http.response.start",
                    "status": 410,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"access-control-allow-origin", b"*"],
                        [b"x-session-expired", b"true"],
                        [b"x-reconnect-required", b"true"],
                    ],
                })
                
                error_body = json.dumps({
                    "error": "session_expired",
                    "message": "Session has expired. Please reconnect to /sse endpoint.",
                    "session_id": self.KNOWN_STALE_SESSION,
                    "reconnect_url": "/sse",
                    "instructions": "Connect to /sse to establish a new session"
                }).encode()
                
                await send({
                    "type": "http.response.body",
                    "body": error_body,
                })
                return
        
        # Pass through to the app
        await self.app(scope, receive, send)

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        """Handle SSE connections with proper error handling"""
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"SSE connection initiated from {client_ip}")
        
        try:
            async with sse.connect_sse(
                    request.scope,
                    request.receive,
                    request._send,  # noqa: SLF001
            ) as (read_stream, write_stream):
                logger.info(f"SSE session established for {client_ip}")
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
        except Exception as e:
            logger.error(f"SSE error for {client_ip}: {str(e)}", exc_info=True)
            # Don't re-raise exceptions to allow graceful shutdown
        finally:
            logger.info(f"SSE connection closed for {client_ip}")
        
        # Critical: Always return a Response object to avoid TypeError
        return Response(status_code=200)

    
    app = Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
            Route("/", endpoint=health_check, methods=["GET"]),
            Route("/health", endpoint=health_check, methods=["GET"]),
            Route("/debug/sse", endpoint=debug_sse, methods=["GET"])
        ],
    )
    
    # Add middlewares - order matters! StaleSessionMiddleware must be first
    app.add_middleware(StaleSessionMiddleware)  # This runs first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description='MCP Server with Mem0')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8080)), help='Port to bind to')
    args = parser.parse_args()

    # Create the app
    starlette_app = create_starlette_app(mcp_server, debug=False)
    
    print(f"\n{'='*50}")
    print(f"🚀 MCP Server with Mem0 - FULL Mode (v{VERSION})")
    print(f"{'='*50}")
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"🔌 SSE Endpoint: http://{args.host}:{args.port}/sse")
    print(f"💚 Health Check: http://{args.host}:{args.port}/health")
    print(f"🛠️  Tools Enabled: 7")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📂 Working Dir: {os.getcwd()}")
    print(f"{'='*50}\n")

    uvicorn.run(starlette_app, host=args.host, port=args.port)