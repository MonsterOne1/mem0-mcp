"""
Centralized mem0 client wrapper with retry logic and error handling
"""
import time
import logging
from typing import Optional, List, Dict, Any, Callable
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Mem0ClientWrapper:
    """Wrapper for mem0 client with retry logic and enhanced functionality"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize mem0 client with optional API key"""
        self.client = MemoryClient(api_key=api_key) if api_key else MemoryClient()
        self.default_user_id = "cursor_mcp"
        
    def retry_operation(self, func: Callable, max_retries: int = 3, retry_delay: float = 1.0) -> Any:
        """
        Retry an operation with exponential backoff
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (doubles each time)
            
        Returns:
            Result of the function or raises the last exception
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
    
    def add_memory(self, content: str, user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add a memory with retry logic
        
        Args:
            content: The content to store
            user_id: User ID (defaults to self.default_user_id)
            metadata: Additional metadata to store
            
        Returns:
            Response from mem0 API
        """
        user_id = user_id or self.default_user_id
        
        def _add():
            messages = [{"role": "user", "content": content}]
            params = {"user_id": user_id, "output_format": "v1.1"}
            if metadata:
                params["metadata"] = metadata
            return self.client.add(messages, **params)
        
        return self.retry_operation(_add)
    
    def search_memories(self, query: str, user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search memories with retry logic
        
        Args:
            query: Search query
            user_id: User ID (defaults to self.default_user_id)
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        user_id = user_id or self.default_user_id
        
        def _search():
            return self.client.search(query, user_id=user_id, limit=limit, output_format="v1.1")
        
        results = self.retry_operation(_search)
        return results.get("results", [])
    
    def get_all_memories(self, user_id: Optional[str] = None, page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
        """
        Get all memories with retry logic
        
        Args:
            user_id: User ID (defaults to self.default_user_id)
            page: Page number
            page_size: Number of items per page
            
        Returns:
            List of all memories
        """
        user_id = user_id or self.default_user_id
        
        def _get_all():
            return self.client.get_all(user_id=user_id, page=page, page_size=page_size)
        
        results = self.retry_operation(_get_all)
        return results.get("results", [])
    
    def update_memory(self, memory_id: str, content: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a memory
        
        Args:
            memory_id: The ID of the memory to update
            content: New content
            user_id: User ID (defaults to self.default_user_id)
            
        Returns:
            Response from mem0 API
        """
        user_id = user_id or self.default_user_id
        
        def _update():
            return self.client.update(memory_id, content, user_id=user_id)
        
        return self.retry_operation(_update)
    
    def delete_memory(self, memory_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a memory
        
        Args:
            memory_id: The ID of the memory to delete
            user_id: User ID (defaults to self.default_user_id)
            
        Returns:
            Response from mem0 API
        """
        user_id = user_id or self.default_user_id
        
        def _delete():
            return self.client.delete(memory_id, user_id=user_id)
        
        return self.retry_operation(_delete)
    
    def get_memory_by_id(self, memory_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: The ID of the memory
            user_id: User ID (defaults to self.default_user_id)
            
        Returns:
            Memory dict or None if not found
        """
        user_id = user_id or self.default_user_id
        
        def _get():
            return self.client.get(memory_id, user_id=user_id)
        
        try:
            return self.retry_operation(_get)
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None
    
    def update_project_instructions(self, instructions: str) -> Dict[str, Any]:
        """
        Update project custom instructions
        
        Args:
            instructions: Custom instructions for the project
            
        Returns:
            Response from mem0 API
        """
        def _update():
            return self.client.update_project(custom_instructions=instructions)
        
        return self.retry_operation(_update)


# Global instance for convenience
_client_instance = None


def get_client() -> Mem0ClientWrapper:
    """Get or create the global mem0 client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = Mem0ClientWrapper()
    return _client_instance