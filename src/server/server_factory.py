"""
Server factory for creating MCP server - Simplified
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route, Mount
import json

from ..tools import MemoryTools
from ..core import get_client

logger = logging.getLogger(__name__)


class ServerFactory:
    """Factory for creating MCP server"""
    
    @staticmethod
    def create_mcp_server(
        name: str = "mem0-mcp",
        custom_instructions: Optional[str] = None
    ) -> FastMCP:
        """
        Create an MCP server with memory tools
        
        Args:
            name: Server name
            custom_instructions: Custom instructions for mem0
            
        Returns:
            Configured FastMCP server
        """
        # Initialize FastMCP server
        mcp = FastMCP(name)
        
        # Initialize mem0 client with custom instructions
        if custom_instructions:
            client = get_client()
            client.update_project_instructions(custom_instructions)
        
        # Initialize memory tools
        tools = MemoryTools()
        
        # Register the 3 core tools
        @mcp.tool(
            description="""Add new information to your personal memory. This tool stores any important information 
            about yourself, your preferences, knowledge, or anything you want me to remember."""
        )
        async def add_memory(text: str) -> str:
            return await tools.add_memory(text)
        
        @mcp.tool(
            description="""Search through stored memories using semantic search. This tool searches 
            for relevant information and context from your memories."""
        )
        async def search_memories(query: str) -> str:
            return await tools.search_memories(query)
        
        @mcp.tool(
            description="""Retrieve all stored memories for the user. Returns a comprehensive list of all stored 
            information."""
        )
        async def get_all_memories() -> str:
            return await tools.get_all_memories()
        
        logger.info(f"Created MCP server '{name}' with {len(mcp._tool_manager._tools)} tools")
        return mcp
    
    @staticmethod
    async def health_check(request: Request) -> Response:
        """Health check endpoint"""
        return Response(
            content=json.dumps({
                "status": "healthy",
                "service": "mem0-mcp",
                "timestamp": datetime.now().isoformat()
            }),
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    @staticmethod
    def create_starlette_app(
        mcp_server: Server,
        debug: bool = False
    ):
        """
        Create a Starlette application that can serve the MCP server with SSE
        
        Args:
            mcp_server: The MCP server instance
            debug: Enable debug mode
            
        Returns:
            Configured Starlette app
        """
        # Create SSE transport
        sse = SseServerTransport("/messages/")
        
        # Create the ASGI app for SSE
        async def sse_app(scope, receive, send):
            """ASGI app that handles both SSE and message endpoints"""
            path = scope.get("path", "")
            
            if path == "/sse" and scope["method"] == "GET":
                # Handle SSE connection
                async with sse.connect_sse(scope, receive, send) as (read_stream, write_stream):
                    await mcp_server.run(
                        read_stream,
                        write_stream,
                        mcp_server.create_initialization_options()
                    )
            elif path.startswith("/messages/"):
                # Delegate to SSE transport's message handler
                await sse.handle_post_message(scope, receive, send)
            elif path in ["/", "/health"]:
                # Health check
                response = await ServerFactory.health_check(Request(scope, receive))
                await response(scope, receive, send)
            else:
                # 404 for unknown paths
                response = Response("Not found", status_code=404)
                await response(scope, receive, send)
        
        # Return the app directly
        return sse_app
    
    @staticmethod
    def create_server(
        name: str = "mem0-mcp",
        custom_instructions: Optional[str] = None,
        debug: bool = False
    ) -> tuple[FastMCP, Starlette]:
        """
        Create both MCP server and Starlette app
        
        Args:
            name: Server name
            custom_instructions: Custom instructions for mem0
            debug: Enable debug mode
            
        Returns:
            Tuple of (MCP server, Starlette app)
        """
        # Create MCP server
        mcp = ServerFactory.create_mcp_server(
            name=name,
            custom_instructions=custom_instructions
        )
        
        # Create Starlette app
        app = ServerFactory.create_starlette_app(
            mcp_server=mcp._mcp_server,
            debug=debug
        )
        
        return mcp, app