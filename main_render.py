from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.responses import Response
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
import os
import argparse

load_dotenv()

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("mem0-mcp")

# Initialize mem0 client and set default user
mem0_client = MemoryClient()
DEFAULT_USER_ID = "cursor_mcp"
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Personal Information: Save important details about the user's preferences, habits, and personal information.
- Knowledge & Facts: Store useful information, facts, and knowledge that might be referenced later.
- Preferences & Settings: Remember user's preferences for various topics, tools, and services.
- Important Dates & Events: Note significant dates, appointments, and events.
- Context & History: Keep track of previous conversations and important context.
- Skills & Expertise: Document user's skills, areas of expertise, and learning goals.
- Relationships & Contacts: Remember information about people, relationships, and contact details.
- Goals & Plans: Store user's goals, plans, and aspirations for future reference.
"""
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)

@mcp.tool(
    description="""Add new information to your personal memory. This tool stores any important information 
    about yourself, your preferences, knowledge, or anything you want me to remember. When storing information, 
    you should include:
    - Personal preferences and habits
    - Important facts and knowledge
    - Contact information and relationships
    - Goals, plans, and aspirations
    - Skills, expertise, and learning interests
    - Important dates and events
    - Context from previous conversations
    - Any other information you want me to remember
    The information will be indexed for semantic search and can be retrieved later using natural language queries"""
)
def add_memory(content: str):
    """
    Store information in mem0 memory
    Args:
        content: The information to remember
    Returns:
        Confirmation that the memory was added
    """
    try:
        # Add memory to mem0 with user context
        response = mem0_client.add(content, user_id=DEFAULT_USER_ID)
        
        if response and hasattr(response, 'id'):
            return f"Successfully stored memory with ID: {response.id}. The information has been indexed and can be retrieved later."
        else:
            return "Memory stored successfully."
    except Exception as e:
        return f"Error storing memory: {str(e)}"

@mcp.tool(
    description="""Retrieve all memories stored for you. This shows everything I remember about you, your preferences, and our conversations."""
)
def get_all_memories():
    """
    Get all memories from mem0
    Returns:
        All stored memories
    """
    try:
        # Get all memories for the user
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        
        if not memories:
            return "No memories found. Start by adding some information you'd like me to remember!"
        
        # Format memories for display
        formatted_memories = []
        for i, memory in enumerate(memories, 1):
            memory_text = memory.get('memory', memory.get('text', 'No content'))
            created_at = memory.get('created_at', 'Unknown time')
            memory_id = memory.get('id', 'No ID')
            formatted_memories.append(
                f"{i}. [{memory_id}] {memory_text}\n   Created: {created_at}"
            )
        
        return "Here are all your stored memories:\n\n" + "\n\n".join(formatted_memories)
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"

@mcp.tool(
    description="""Search through your memories using natural language. Find specific information, preferences, or past conversations."""
)
def search_memories(query: str):
    """
    Search memories semantically
    Args:
        query: Natural language search query
    Returns:
        Relevant memories matching the query
    """
    try:
        # Search memories for the user
        results = mem0_client.search(query, user_id=DEFAULT_USER_ID, limit=10)
        
        if not results:
            return f"No memories found matching '{query}'. Try a different search term or check all memories."
        
        # Format search results
        formatted_results = []
        for i, result in enumerate(results, 1):
            memory_text = result.get('memory', result.get('text', 'No content'))
            score = result.get('score', 0)
            created_at = result.get('created_at', 'Unknown time')
            memory_id = result.get('id', 'No ID')
            formatted_results.append(
                f"{i}. [{memory_id}] (Relevance: {score:.2f}) {memory_text}\n   Created: {created_at}"
            )
        
        return f"Found {len(results)} memories matching '{query}':\n\n" + "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

# Create SSE transport handler
async def handle_sse(request: Request):
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return Response(
            content="",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    
    # Handle GET request with info
    if request.method == "GET":
        return Response(
            content="mem0-mcp SSE endpoint is running. Use POST method to connect.",
            headers={
                "Content-Type": "text/plain",
                "Access-Control-Allow-Origin": "*",
            }
        )
    
    # Handle POST for SSE
    sse_transport = SseServerTransport("/messages/")
    
    async with sse_transport.connect_sse(
        request.scope,
        request.receive,
        request.send,
    ) as (read_stream, write_stream):
        # Get the MCP server instance
        server = mcp._mcp_server
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

# Create health check endpoint
async def health_check(request: Request):
    return Response(
        content=json.dumps({"status": "healthy", "service": "mem0-mcp"}),
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Create Starlette app with routes
sse_transport = SseServerTransport("/messages/")
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["POST", "GET", "OPTIONS"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
        Route("/", endpoint=health_check, methods=["GET"]),
        Route("/health", endpoint=health_check, methods=["GET"])
    ]
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MCP Server with Mem0')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8080)), help='Port to bind to')
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print(f"Starting MCP server with mem0 on {args.host}:{args.port}")
    print(f"SSE endpoint available at http://{args.host}:{args.port}/sse")
    print(f"Health check available at http://{args.host}:{args.port}/health")
    
    uvicorn.run(app, host=args.host, port=args.port)