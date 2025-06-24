from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json

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
    The information will be indexed for semantic search and can be retrieved later using natural language queries."""
)
async def add_memory(text: str) -> str:
    """Add new information to personal memory.

    This tool is designed to store any important information about yourself, your preferences, 
    knowledge, or anything you want me to remember. It can include:
    - Personal information and preferences
    - Knowledge and facts
    - Important dates and events
    - Skills and expertise
    - Goals and plans
    - Context from conversations

    Args:
        text: The content to store in memory, including any information you want me to remember
    """
    try:
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1")
        return f"Successfully added to memory: {text}"
    except Exception as e:
        return f"Error adding to memory: {str(e)}"

@mcp.tool(
    description="""Retrieve all stored memories for the user. Call this tool when you need 
    complete context of all previously stored information. This is useful when:
    - You need to review all available information about the user
    - You want to check all stored preferences and details
    - You need to get a comprehensive overview of the user's information
    - You want to ensure no relevant information is missed
    Returns a comprehensive list of:
    - Personal information and preferences
    - Knowledge and facts
    - Important dates and events
    - Skills and expertise
    - Goals and plans
    Results are returned in JSON format with metadata."""
)
async def get_all_memories() -> str:
    """Get all stored memories for the user.

    Returns a JSON formatted list of all stored information, including:
    - Personal information and preferences
    - Knowledge and facts
    - Important dates and events
    - Skills and expertise
    - Goals and plans
    Each memory includes metadata about when it was created and its content type.
    """
    try:
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=50)
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error getting memories: {str(e)}"

@mcp.tool(
    description="""Search through stored memories using semantic search. This tool should be called 
    for EVERY user query to find relevant information and context. It helps find:
    - Personal information and preferences
    - Knowledge and facts
    - Important dates and events
    - Skills and expertise
    - Goals and plans
    - Context from previous conversations
    The search uses natural language understanding to find relevant matches, so you can
    describe what you're looking for in plain English. Always search the memories before 
    providing answers to ensure you leverage existing knowledge about the user."""
)
async def search_memories(query: str) -> str:
    """Search memories using semantic search.

    The search is powered by natural language understanding, allowing you to find:
    - Personal information and preferences
    - Knowledge and facts
    - Important dates and events
    - Skills and expertise
    - Goals and plans
    - Context from previous conversations
    Results are ranked by relevance to your query.

    Args:
        query: Search query string describing what you're looking for. Can be natural language
              or specific terms.
    """
    try:
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, output_format="v1.1")
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
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

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
