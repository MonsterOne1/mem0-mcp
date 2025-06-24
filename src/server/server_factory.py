"""
Server factory for creating MCP servers with different configurations
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
    """Factory for creating MCP servers with different configurations"""
    
    @staticmethod
    def create_mcp_server(
        name: str = "mem0-mcp",
        enable_advanced_tools: bool = True,
        custom_instructions: Optional[str] = None
    ) -> FastMCP:
        """
        Create an MCP server with memory tools
        
        Args:
            name: Server name
            enable_advanced_tools: Whether to enable advanced tools
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
        
        # Register basic tools (always enabled)
        @mcp.tool(
            description="""Add new information to your personal memory. This tool stores any important information 
            about yourself, your preferences, knowledge, or anything you want me to remember."""
        )
        async def add_memory(text: str) -> str:
            return await tools.add_memory(text)
        
        @mcp.tool(
            description="""Retrieve all stored memories for the user. Returns a comprehensive list of all stored 
            information including personal details, preferences, knowledge, and more."""
        )
        async def get_all_memories() -> str:
            return await tools.get_all_memories()
        
        @mcp.tool(
            description="""Search through stored memories using semantic search. This tool should be called 
            for EVERY user query to find relevant information and context."""
        )
        async def search_memories(query: str) -> str:
            return await tools.search_memories(query)
        
        # Register advanced tools if enabled
        if enable_advanced_tools:
            @mcp.tool(
                description="Update an existing memory with new content"
            )
            def update_memory(memory_id: str, new_content: str) -> str:
                return tools.update_memory(memory_id, new_content)
            
            @mcp.tool(
                description="Delete a specific memory by ID"
            )
            def delete_memory(memory_id: str) -> str:
                return tools.delete_memory(memory_id)
            
            @mcp.tool(
                description="Advanced search with filtering by category and relevance score"
            )
            def advanced_search_memories(
                query: Optional[str] = None,
                category: Optional[str] = None,
                limit: int = 20,
                min_score: float = 0.0
            ) -> str:
                return tools.advanced_search_memories(query, category, limit, min_score)
            
            @mcp.tool(
                description="Get statistics about stored memories including counts by category"
            )
            def get_memory_stats() -> str:
                return tools.get_memory_stats()
            
            @mcp.tool(
                description="Analyze patterns and insights from stored memories"
            )
            def analyze_memories() -> str:
                return tools.analyze_memories()
            
            @mcp.tool(
                description="Get memories by category or list available categories"
            )
            def get_memories_by_category(category: Optional[str] = None) -> str:
                return tools.get_memories_by_category(category)
            
            @mcp.tool(
                description="Export all memories in a structured format"
            )
            def export_memories(include_metadata: bool = True) -> str:
                return tools.export_memories(include_metadata)
            
            @mcp.tool(
                description="Quick check for relevant memories about a topic"
            )
            def check_relevant_memories(topic: str) -> str:
                return tools.check_relevant_memories(topic)
        
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
        debug: bool = False,
        include_health: bool = True
    ) -> Starlette:
        """
        Create a Starlette application that can serve the MCP server with SSE
        
        Args:
            mcp_server: The MCP server instance
            debug: Enable debug mode
            include_health: Include health check endpoints
            
        Returns:
            Configured Starlette app
        """
        sse = SseServerTransport("/messages/")
        
        async def handle_sse(request: Request) -> None:
            """Handle SSE connections"""
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
        
        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]
        
        if include_health:
            routes.extend([
                Route("/", endpoint=ServerFactory.health_check, methods=["GET"]),
                Route("/health", endpoint=ServerFactory.health_check, methods=["GET"])
            ])
        
        return Starlette(debug=debug, routes=routes)
    
    @staticmethod
    def create_server(
        mode: str = "full",
        name: str = "mem0-mcp",
        custom_instructions: Optional[str] = None,
        debug: bool = False
    ) -> tuple[FastMCP, Starlette]:
        """
        Create both MCP server and Starlette app
        
        Args:
            mode: "basic" or "full" - determines which tools to enable
            name: Server name
            custom_instructions: Custom instructions for mem0
            debug: Enable debug mode
            
        Returns:
            Tuple of (MCP server, Starlette app)
        """
        # Create MCP server
        enable_advanced = mode == "full"
        mcp = ServerFactory.create_mcp_server(
            name=name,
            enable_advanced_tools=enable_advanced,
            custom_instructions=custom_instructions
        )
        
        # Create Starlette app
        app = ServerFactory.create_starlette_app(
            mcp_server=mcp._mcp_server,
            debug=debug,
            include_health=True
        )
        
        return mcp, app