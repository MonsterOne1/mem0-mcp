"""
Unified memory tools for MCP server
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core import get_client, MemoryCategories

logger = logging.getLogger(__name__)


class MemoryTools:
    """Collection of all memory-related tools"""
    
    def __init__(self):
        self.client = get_client()
        self.categories = MemoryCategories()
    
    # Basic Tools (from main.py)
    
    async def add_memory(self, text: str) -> str:
        """
        Add new information to personal memory
        
        This tool stores any important information about yourself, your preferences,
        knowledge, or anything you want me to remember.
        """
        try:
            # Auto-categorize the memory
            categories = self.categories.categorize(text)
            tagged_text = self.categories.format_with_tags(text, categories)
            
            # Add metadata
            metadata = {
                "categories": categories,
                "timestamp": datetime.now().isoformat()
            }
            
            self.client.add_memory(tagged_text, metadata=metadata)
            return f"Successfully added to memory: {text}"
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return f"Error adding to memory: {str(e)}"
    
    async def get_all_memories(self) -> str:
        """
        Get all stored memories for the user
        
        Returns a comprehensive list of all stored information including
        personal details, preferences, knowledge, and more.
        """
        try:
            memories = self.client.get_all_memories()
            flattened = [m.get("memory", m) for m in memories]
            return json.dumps(flattened, indent=2)
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return f"Error getting memories: {str(e)}"
    
    async def search_memories(self, query: str) -> str:
        """
        Search through stored memories using semantic search
        
        This tool should be called for EVERY user query to find relevant
        information and context.
        """
        try:
            memories = self.client.search_memories(query)
            flattened = [m.get("memory", m) for m in memories]
            return json.dumps(flattened, indent=2)
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return f"Error searching memories: {str(e)}"
    
    # Advanced Tools (from main_render.py)
    
    def update_memory(self, memory_id: str, new_content: str) -> str:
        """
        Update an existing memory with new content
        
        Args:
            memory_id: The ID of the memory to update
            new_content: The new content to replace the old one
        """
        try:
            # Auto-categorize the new content
            categories = self.categories.categorize(new_content)
            tagged_content = self.categories.format_with_tags(new_content, categories)
            
            self.client.update_memory(memory_id, tagged_content)
            return f"Successfully updated memory {memory_id}"
        except Exception as e:
            logger.error(f"Error updating memory {memory_id}: {e}")
            return f"Error updating memory: {str(e)}"
    
    def delete_memory(self, memory_id: str) -> str:
        """
        Delete a specific memory by ID
        
        Args:
            memory_id: The ID of the memory to delete
        """
        try:
            self.client.delete_memory(memory_id)
            return f"Successfully deleted memory {memory_id}"
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return f"Error deleting memory: {str(e)}"
    
    def advanced_search_memories(
        self, 
        query: Optional[str] = None, 
        category: Optional[str] = None,
        limit: int = 20,
        min_score: float = 0.0
    ) -> str:
        """
        Advanced search with filtering options
        
        Args:
            query: Search query (optional)
            category: Filter by category (optional)
            limit: Maximum number of results
            min_score: Minimum relevance score
        """
        try:
            if query:
                memories = self.client.search_memories(query, limit=limit)
            else:
                memories = self.client.get_all_memories(page_size=limit)
            
            # Filter by category if specified
            if category:
                filtered = []
                for memory in memories:
                    content = memory.get("memory", "")
                    _, tags = self.categories.extract_tags(content)
                    if category in tags:
                        filtered.append(memory)
                memories = filtered
            
            # Filter by score if searching
            if query and min_score > 0:
                memories = [m for m in memories if m.get("score", 1.0) >= min_score]
            
            return json.dumps(memories, indent=2)
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return f"Error searching memories: {str(e)}"
    
    def get_memory_stats(self) -> str:
        """
        Get statistics about stored memories
        
        Returns counts by category and other useful metrics
        """
        try:
            all_memories = self.client.get_all_memories(page_size=100)
            
            stats = {
                "total_memories": len(all_memories),
                "categories": {},
                "recent_memories": 0,
                "oldest_memory": None,
                "newest_memory": None
            }
            
            # Analyze categories
            for memory in all_memories:
                content = memory.get("memory", "")
                _, tags = self.categories.extract_tags(content)
                
                for tag in tags:
                    stats["categories"][tag] = stats["categories"].get(tag, 0) + 1
                
                # Track dates
                created = memory.get("created_at")
                if created:
                    if not stats["oldest_memory"] or created < stats["oldest_memory"]:
                        stats["oldest_memory"] = created
                    if not stats["newest_memory"] or created > stats["newest_memory"]:
                        stats["newest_memory"] = created
            
            return json.dumps(stats, indent=2)
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return f"Error getting memory statistics: {str(e)}"
    
    def analyze_memories(self) -> str:
        """
        Analyze patterns and insights from stored memories
        
        Provides a summary of memory patterns and key themes
        """
        try:
            memories = self.client.get_all_memories(page_size=100)
            
            analysis = {
                "total_memories": len(memories),
                "category_distribution": {},
                "common_themes": [],
                "memory_timeline": {},
                "insights": []
            }
            
            # Category distribution
            categories_count = {}
            for memory in memories:
                content = memory.get("memory", "")
                _, tags = self.categories.extract_tags(content)
                for tag in tags:
                    categories_count[tag] = categories_count.get(tag, 0) + 1
            
            # Sort categories by frequency
            analysis["category_distribution"] = dict(
                sorted(categories_count.items(), key=lambda x: x[1], reverse=True)
            )
            
            # Generate insights
            if len(memories) > 10:
                analysis["insights"].append("You have a substantial memory collection")
            
            top_category = max(categories_count.items(), key=lambda x: x[1])[0] if categories_count else None
            if top_category:
                desc = self.categories.get_category_description(top_category)
                analysis["insights"].append(f"Most memories are about: {desc}")
            
            return json.dumps(analysis, indent=2)
        except Exception as e:
            logger.error(f"Error analyzing memories: {e}")
            return f"Error analyzing memories: {str(e)}"
    
    def get_memories_by_category(self, category: Optional[str] = None) -> str:
        """
        Get all memories in a specific category
        
        Args:
            category: Category name (shows available categories if None)
        """
        try:
            if not category:
                # Return available categories
                categories = list(self.categories.CATEGORY_KEYWORDS.keys())
                return json.dumps({
                    "available_categories": categories,
                    "descriptions": {
                        cat: self.categories.get_category_description(cat)
                        for cat in categories
                    }
                }, indent=2)
            
            # Get memories in the specified category
            all_memories = self.client.get_all_memories(page_size=100)
            filtered = []
            
            for memory in all_memories:
                content = memory.get("memory", "")
                _, tags = self.categories.extract_tags(content)
                if category in tags:
                    filtered.append(memory)
            
            return json.dumps({
                "category": category,
                "description": self.categories.get_category_description(category),
                "count": len(filtered),
                "memories": filtered
            }, indent=2)
        except Exception as e:
            logger.error(f"Error getting memories by category: {e}")
            return f"Error: {str(e)}"
    
    def export_memories(self, include_metadata: bool = True) -> str:
        """
        Export all memories in a structured format
        
        Args:
            include_metadata: Whether to include metadata in export
        """
        try:
            memories = self.client.get_all_memories(page_size=100)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_memories": len(memories),
                "memories": []
            }
            
            for memory in memories:
                entry = {
                    "id": memory.get("id"),
                    "content": memory.get("memory", ""),
                    "created_at": memory.get("created_at")
                }
                
                if include_metadata:
                    _, tags = self.categories.extract_tags(entry["content"])
                    entry["categories"] = tags
                    entry["metadata"] = memory.get("metadata", {})
                
                export_data["memories"].append(entry)
            
            return json.dumps(export_data, indent=2)
        except Exception as e:
            logger.error(f"Error exporting memories: {e}")
            return f"Error exporting memories: {str(e)}"
    
    def check_relevant_memories(self, topic: str) -> str:
        """
        Quick check for relevant memories about a topic
        
        Args:
            topic: The topic or context to check memories for
        """
        try:
            # Quick search with limited results
            memories = self.client.search_memories(topic, limit=5)
            
            if not memories:
                return "No relevant memories found for this topic."
            
            summary = f"Found {len(memories)} relevant memories:\n"
            for i, memory in enumerate(memories, 1):
                content = memory.get("memory", "")
                # Truncate long memories
                if len(content) > 100:
                    content = content[:97] + "..."
                summary += f"{i}. {content}\n"
            
            return summary
        except Exception as e:
            logger.error(f"Error checking memories: {e}")
            return f"Error checking memories: {str(e)}"


# Tool registry for easy access
def get_memory_tools() -> Dict[str, Any]:
    """Get all memory tools as a dictionary"""
    tools = MemoryTools()
    
    return {
        # Basic tools
        "add_memory": tools.add_memory,
        "get_all_memories": tools.get_all_memories,
        "search_memories": tools.search_memories,
        
        # Advanced tools
        "update_memory": tools.update_memory,
        "delete_memory": tools.delete_memory,
        "advanced_search_memories": tools.advanced_search_memories,
        "get_memory_stats": tools.get_memory_stats,
        "analyze_memories": tools.analyze_memories,
        "get_memories_by_category": tools.get_memories_by_category,
        "export_memories": tools.export_memories,
        "check_relevant_memories": tools.check_relevant_memories
    }