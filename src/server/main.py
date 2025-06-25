"""
MCP server for mem0 - Simplified version
"""
import os
import sys
import argparse
import logging
import uvicorn
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.server.server_factory import ServerFactory

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default custom instructions
DEFAULT_INSTRUCTIONS = """
Extract and remember the following information:
- Personal Information: Save important details about the user's preferences, habits, and personal information.
- Knowledge & Facts: Store useful information, facts, and knowledge that might be referenced later.
- Important Context: Keep track of important context and information from conversations.
"""


def main():
    parser = argparse.ArgumentParser(description='MCP Server with Mem0')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to bind to')
    parser.add_argument('--port', type=int, default=None,
                        help='Port to bind to (default: from PORT env or 8080)')
    parser.add_argument('--name', type=str, default='mem0-mcp',
                        help='Server name')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--no-instructions', action='store_true',
                        help='Disable custom instructions')
    
    args = parser.parse_args()
    
    # Determine port
    if args.port is None:
        args.port = int(os.environ.get('PORT', 8080))
    
    # Set custom instructions
    custom_instructions = None if args.no_instructions else DEFAULT_INSTRUCTIONS
    
    # Create server
    logger.info(f"Creating MCP server '{args.name}'...")
    mcp, app = ServerFactory.create_server(
        name=args.name,
        custom_instructions=custom_instructions,
        debug=args.debug
    )
    
    # Log server information
    logger.info(f"Server created with {len(mcp._tool_manager._tools)} tools")
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"SSE endpoint: http://{args.host}:{args.port}/sse")
    logger.info(f"Health check: http://{args.host}:{args.port}/health")
    
    # Print user-friendly startup message
    print("\n" + "="*50)
    print(f"🚀 MCP Server with Mem0")
    print("="*50)
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"🔌 SSE Endpoint: http://{args.host}:{args.port}/sse")
    print(f"💚 Health Check: http://{args.host}:{args.port}/health")
    print(f"🛠️  Tools Enabled: {len(mcp._tool_manager._tools)}")
    print("="*50 + "\n")
    
    # Run server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info",
        access_log=True
    )


if __name__ == "__main__":
    main()