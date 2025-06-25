"""
Memory tools for MCP server - Simplified to core functionality
"""
import json
import logging
from typing import List, Dict, Any

from ..core import get_client

logger = logging.getLogger(__name__)


class MemoryTools:
    """Core memory tools for MCP server"""
    
    def __init__(self):
        self.client = get_client()
    
    async def add_memory(self, text: str) -> str:
        """
        Add new information to personal memory
        
        This tool stores any important information about yourself, your preferences,
        knowledge, or anything you want me to remember.
        """
        try:
            self.client.add_memory(text)
            return f"Successfully added to memory: {text}"
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return f"Error adding to memory: {str(e)}"
    
    async def search_memories(self, query: str) -> str:
        """
        Search through stored memories using semantic search
        
        This tool searches for relevant information and context from your memories.
        """
        try:
            memories = self.client.search_memories(query)
            flattened = [m.get("memory", m) for m in memories]
            return json.dumps(flattened, indent=2)
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return f"Error searching memories: {str(e)}"
    
    async def get_all_memories(self) -> str:
        """
        Get all stored memories for the user
        
        Returns a comprehensive list of all stored information.
        """
        try:
            memories = self.client.get_all_memories()
            flattened = [m.get("memory", m) for m in memories]
            return json.dumps(flattened, indent=2)
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return f"Error getting memories: {str(e)}"


# Tool registry for easy access
def get_memory_tools() -> Dict[str, Any]:
    """Get all memory tools as a dictionary"""
    tools = MemoryTools()
    
    return {
        "add_memory": tools.add_memory,
        "search_memories": tools.search_memories,
        "get_all_memories": tools.get_all_memories,
    }