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

# Helper function for retry logic
import time
import logging

logger = logging.getLogger(__name__)

def retry_operation(func, max_retries=3, retry_delay=1.0):
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

# Category detection system
CATEGORY_KEYWORDS = {
    "personal_info": ["name", "birthday", "age", "live", "from", "born", "address", "phone", "email"],
    "work": ["work", "job", "company", "career", "office", "profession", "colleague", "boss", "employee"],
    "relationships": ["friend", "family", "wife", "husband", "child", "parent", "sibling", "partner", "mother", "father"],
    "goals": ["goal", "plan", "want", "wish", "dream", "aspire", "aim", "objective", "target", "ambition"],
    "knowledge": ["know", "learn", "understand", "fact", "information", "study", "research", "discover"],
    "skills": ["skill", "able", "can", "speak", "language", "expertise", "proficient", "experienced"],
    "dates_events": ["date", "event", "meeting", "appointment", "schedule", "calendar", "tomorrow", "yesterday", "today", "week", "month", "year"],
    "preferences": ["like", "prefer", "favorite", "enjoy", "love", "hate", "dislike", "interest"],
    "health": ["health", "medical", "doctor", "medicine", "sick", "exercise", "diet", "sleep"],
    "hobbies": ["hobby", "fun", "play", "game", "sport", "music", "art", "travel", "read", "watch"]
}

def categorize_memory(content: str):
    """
    Automatically categorize a memory based on its content
    Args:
        content: The memory content to categorize
    Returns:
        List of applicable categories
    """
    content_lower = content.lower()
    categories = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in content_lower for keyword in keywords):
            categories.append(category)
    
    # If no category matches, mark as "other"
    if not categories:
        categories.append("other")
    
    return categories

def format_memory_with_tags(content: str, categories: list):
    """
    Format memory content with category tags
    Args:
        content: Original memory content
        categories: List of categories
    Returns:
        Formatted memory string with tags
    """
    if categories and categories != ["other"]:
        tags = " ".join([f"#{cat}" for cat in categories])
        return f"{content} [{tags}]"
    return content
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

# Create global SSE transport instance
sse_transport = SseServerTransport("/messages/")

@mcp.tool(
    description="""Check if there are relevant memories before answering questions. This tool should be used proactively to provide context-aware responses. It quickly checks for memories related to the current topic and returns a summary."""
)
def check_relevant_memories(topic: str):
    """
    Quick check for relevant memories about a topic
    Args:
        topic: The topic or context to check memories for
    Returns:
        Brief summary of relevant memories or indication that none exist
    """
    try:
        # Search for relevant memories
        results = retry_operation(
            lambda: mem0_client.search(topic, user_id=DEFAULT_USER_ID, limit=5),
            max_retries=2,
            retry_delay=0.5
        )
        
        if not results:
            return f"No specific memories found about '{topic}'."
        
        # Summarize findings
        summary = f"Found {len(results)} relevant memories about '{topic}':\n"
        for i, result in enumerate(results, 1):
            memory_text = result.get('memory', result.get('text', 'No content'))
            score = result.get('score', 0)
            if score > 0.7:  # Only include highly relevant memories
                summary += f"• {memory_text}\n"
        
        return summary
    except Exception as e:
        logger.warning(f"Quick memory check failed: {str(e)}")
        return "Could not check memories at this time."

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
    Store information in mem0 memory with automatic categorization
    Args:
        content: The information to remember
    Returns:
        Confirmation that the memory was added with categories
    """
    try:
        # Automatically categorize the memory
        categories = categorize_memory(content)
        
        # Format content with tags
        tagged_content = format_memory_with_tags(content, categories)
        
        # Add memory to mem0 with user context using retry logic
        response = retry_operation(
            lambda: mem0_client.add(tagged_content, user_id=DEFAULT_USER_ID),
            max_retries=3,
            retry_delay=1.0
        )
        
        if response and hasattr(response, 'id'):
            category_info = f" (Categories: {', '.join(categories)})" if categories != ["other"] else ""
            return f"Successfully stored memory with ID: {response.id}{category_info}. The information has been indexed and can be retrieved later."
        else:
            category_info = f" (Categories: {', '.join(categories)})" if categories != ["other"] else ""
            return f"Memory stored successfully{category_info}."
    except Exception as e:
        logger.error(f"Failed to add memory after retries: {str(e)}")
        return f"Error storing memory: {str(e)}. Please try again later."

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
        # Get all memories for the user with retry logic
        memories = retry_operation(
            lambda: mem0_client.get_all(user_id=DEFAULT_USER_ID),
            max_retries=3,
            retry_delay=1.0
        )
        
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
        logger.error(f"Failed to get all memories after retries: {str(e)}")
        return f"Error retrieving memories: {str(e)}. Please try again later."

@mcp.tool(
    description="""IMPORTANT: Use this tool FIRST before answering any question about the user. Search through stored memories using natural language to find relevant information, preferences, or past conversations. This helps provide personalized and context-aware responses. Returns up to 10 most relevant results."""
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
        # Search memories for the user with retry logic
        results = retry_operation(
            lambda: mem0_client.search(query, user_id=DEFAULT_USER_ID, limit=10),
            max_retries=3,
            retry_delay=1.0
        )
        
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
        logger.error(f"Failed to search memories after retries: {str(e)}")
        return f"Error searching memories: {str(e)}. Please try again later."

@mcp.tool(
    description="""Advanced memory search with more options. Search by category, limit results, or filter by relevance score. Categories include: personal_info, work, relationships, goals, knowledge, skills, dates_events, preferences, other."""
)
def advanced_search_memories(
    query: str = None,
    category: str = None,
    limit: int = 20,
    min_score: float = 0.0
):
    """
    Advanced search with filtering options
    Args:
        query: Natural language search query (optional if category is provided)
        category: Filter by category (personal_info, work, relationships, goals, knowledge, skills, dates_events, preferences, other)
        limit: Maximum number of results to return (default 20)
        min_score: Minimum relevance score (0.0 to 1.0)
    Returns:
        Filtered memories matching the criteria
    """
    try:
        # Define category keywords for filtering
        category_keywords = {
            "personal_info": ["name", "birthday", "age", "live", "from", "born"],
            "work": ["work", "job", "company", "career", "office", "profession"],
            "relationships": ["friend", "family", "wife", "husband", "child", "parent", "colleague"],
            "goals": ["goal", "plan", "want", "wish", "dream", "aspire", "aim"],
            "knowledge": ["know", "learn", "understand", "fact", "information", "study"],
            "skills": ["skill", "able", "can", "speak", "language", "expertise"],
            "dates_events": ["date", "event", "meeting", "appointment", "schedule", "calendar"],
            "preferences": ["like", "prefer", "favorite", "enjoy", "love", "hate", "dislike"],
            "other": []
        }
        
        # If category is specified but no query, use category keywords
        if category and not query:
            if category in category_keywords:
                query = " OR ".join(category_keywords[category])
            else:
                return f"Invalid category '{category}'. Valid categories: {', '.join(category_keywords.keys())}"
        
        # If neither query nor category is provided, get all memories
        if not query:
            memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
            results = [{"memory": m.get("memory", m.get("text", "")), 
                       "id": m.get("id", ""), 
                       "created_at": m.get("created_at", ""),
                       "score": 1.0} for m in memories[:limit]]
        else:
            # Search with the query
            results = mem0_client.search(query, user_id=DEFAULT_USER_ID, limit=limit * 2)  # Get more to filter
        
        if not results:
            return f"No memories found matching your criteria."
        
        # Filter by category if specified
        if category and category != "other":
            keywords = category_keywords.get(category, [])
            filtered_results = []
            for result in results:
                memory_text = result.get('memory', result.get('text', '')).lower()
                if any(keyword in memory_text for keyword in keywords):
                    filtered_results.append(result)
            results = filtered_results
        
        # Filter by minimum score
        results = [r for r in results if r.get('score', 1.0) >= min_score]
        
        # Limit results
        results = results[:limit]
        
        if not results:
            return f"No memories found matching your criteria. Try adjusting the filters."
        
        # Format search results
        formatted_results = []
        for i, result in enumerate(results, 1):
            memory_text = result.get('memory', result.get('text', 'No content'))
            score = result.get('score', 1.0)
            created_at = result.get('created_at', 'Unknown time')
            memory_id = result.get('id', 'No ID')
            formatted_results.append(
                f"{i}. [{memory_id}] (Relevance: {score:.2f}) {memory_text}\n   Created: {created_at}"
            )
        
        header = f"Found {len(results)} memories"
        if category:
            header += f" in category '{category}'"
        if query and category:
            header += f" matching '{query}'"
        elif query:
            header += f" matching '{query}'"
        
        return f"{header}:\n\n" + "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error in advanced search: {str(e)}"

@mcp.tool(
    description="""Update an existing memory by its ID. First use search_memories or get_all_memories to find the memory ID, then update its content."""
)
def update_memory(memory_id: str, new_content: str):
    """
    Update an existing memory
    Args:
        memory_id: The ID of the memory to update
        new_content: The new content for the memory
    Returns:
        Confirmation that the memory was updated
    """
    try:
        # Update memory using mem0 client with retry logic
        response = retry_operation(
            lambda: mem0_client.update(memory_id, new_content, user_id=DEFAULT_USER_ID),
            max_retries=3,
            retry_delay=1.0
        )
        
        if response:
            return f"Successfully updated memory [{memory_id}] with new content: {new_content}"
        else:
            return f"Failed to update memory [{memory_id}]. Please check if the memory ID is correct."
    except Exception as e:
        logger.error(f"Failed to update memory after retries: {str(e)}")
        return f"Error updating memory: {str(e)}. Please try again later."

@mcp.tool(
    description="""Delete a specific memory by its ID. First use search_memories or get_all_memories to find the memory ID, then delete it. This action cannot be undone."""
)
def delete_memory(memory_id: str):
    """
    Delete a specific memory
    Args:
        memory_id: The ID of the memory to delete
    Returns:
        Confirmation that the memory was deleted
    """
    try:
        # Delete memory using mem0 client with retry logic
        response = retry_operation(
            lambda: mem0_client.delete(memory_id, user_id=DEFAULT_USER_ID),
            max_retries=3,
            retry_delay=1.0
        )
        
        if response:
            return f"Successfully deleted memory [{memory_id}]. This action cannot be undone."
        else:
            return f"Failed to delete memory [{memory_id}]. Please check if the memory ID is correct."
    except Exception as e:
        logger.error(f"Failed to delete memory after retries: {str(e)}")
        return f"Error deleting memory: {str(e)}. Please try again later."

@mcp.tool(
    description="""Get statistics about your stored memories including total count, categories breakdown, and recent activity."""
)
def get_memory_stats():
    """
    Get memory statistics and insights
    Returns:
        Statistics about stored memories
    """
    try:
        # Get all memories
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        
        if not memories:
            return "No memories found. Start adding some information for me to remember!"
        
        # Calculate statistics
        total_count = len(memories)
        
        # Category keywords for classification
        category_keywords = {
            "personal_info": ["name", "birthday", "age", "live", "from", "born"],
            "work": ["work", "job", "company", "career", "office", "profession"],
            "relationships": ["friend", "family", "wife", "husband", "child", "parent", "colleague"],
            "goals": ["goal", "plan", "want", "wish", "dream", "aspire", "aim"],
            "knowledge": ["know", "learn", "understand", "fact", "information", "study"],
            "skills": ["skill", "able", "can", "speak", "language", "expertise"],
            "dates_events": ["date", "event", "meeting", "appointment", "schedule", "calendar"],
            "preferences": ["like", "prefer", "favorite", "enjoy", "love", "hate", "dislike"]
        }
        
        # Count memories by category
        category_counts = {cat: 0 for cat in category_keywords}
        category_counts["other"] = 0
        
        # Analyze each memory
        for memory in memories:
            memory_text = memory.get('memory', memory.get('text', '')).lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in memory_text for keyword in keywords):
                    category_counts[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                category_counts["other"] += 1
        
        # Get recent memories (last 5)
        recent_memories = memories[-5:] if len(memories) > 5 else memories
        
        # Format statistics
        stats_output = f"📊 Memory Statistics\n"
        stats_output += f"{'='*30}\n\n"
        stats_output += f"Total Memories: {total_count}\n\n"
        
        stats_output += f"📂 Categories Breakdown:\n"
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / total_count) * 100
                category_name = category.replace('_', ' ').title()
                stats_output += f"  • {category_name}: {count} ({percentage:.1f}%)\n"
        
        stats_output += f"\n📅 Recent Memories:\n"
        for i, memory in enumerate(recent_memories, 1):
            memory_text = memory.get('memory', memory.get('text', 'No content'))[:50]
            if len(memory_text) == 50:
                memory_text += "..."
            stats_output += f"  {i}. {memory_text}\n"
        
        return stats_output
    except Exception as e:
        return f"Error getting memory statistics: {str(e)}"

@mcp.tool(
    description="""Analyze your memories to find patterns, insights, and generate a summary of what I know about you."""
)
def analyze_memories():
    """
    Analyze memories for patterns and insights
    Returns:
        Analysis and summary of memories
    """
    try:
        # Get all memories
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        
        if not memories:
            return "No memories found to analyze. Start adding some information for me to remember!"
        
        # Categorize and analyze memories
        categories = {
            "personal_info": {"keywords": ["name", "birthday", "age", "live", "from", "born"], "memories": []},
            "work": {"keywords": ["work", "job", "company", "career", "office", "profession"], "memories": []},
            "relationships": {"keywords": ["friend", "family", "wife", "husband", "child", "parent", "colleague"], "memories": []},
            "goals": {"keywords": ["goal", "plan", "want", "wish", "dream", "aspire", "aim"], "memories": []},
            "knowledge": {"keywords": ["know", "learn", "understand", "fact", "information", "study"], "memories": []},
            "skills": {"keywords": ["skill", "able", "can", "speak", "language", "expertise"], "memories": []},
            "dates_events": {"keywords": ["date", "event", "meeting", "appointment", "schedule", "calendar"], "memories": []},
            "preferences": {"keywords": ["like", "prefer", "favorite", "enjoy", "love", "hate", "dislike"], "memories": []}
        }
        
        # Categorize each memory
        uncategorized = []
        for memory in memories:
            memory_text = memory.get('memory', memory.get('text', ''))
            memory_lower = memory_text.lower()
            categorized = False
            
            for category, data in categories.items():
                if any(keyword in memory_lower for keyword in data["keywords"]):
                    data["memories"].append(memory_text)
                    categorized = True
                    break
            
            if not categorized:
                uncategorized.append(memory_text)
        
        # Generate analysis
        analysis = f"🧠 Memory Analysis & Summary\n"
        analysis += f"{'='*40}\n\n"
        
        # Personal Profile
        if categories["personal_info"]["memories"]:
            analysis += f"👤 Personal Profile:\n"
            for mem in categories["personal_info"]["memories"][:3]:
                analysis += f"  • {mem}\n"
            analysis += "\n"
        
        # Skills & Expertise
        if categories["skills"]["memories"]:
            analysis += f"💪 Skills & Expertise:\n"
            for mem in categories["skills"]["memories"][:3]:
                analysis += f"  • {mem}\n"
            analysis += "\n"
        
        # Goals & Aspirations
        if categories["goals"]["memories"]:
            analysis += f"🎯 Goals & Aspirations:\n"
            for mem in categories["goals"]["memories"][:3]:
                analysis += f"  • {mem}\n"
            analysis += "\n"
        
        # Preferences
        if categories["preferences"]["memories"]:
            analysis += f"❤️ Preferences & Interests:\n"
            for mem in categories["preferences"]["memories"][:3]:
                analysis += f"  • {mem}\n"
            analysis += "\n"
        
        # Relationships
        if categories["relationships"]["memories"]:
            analysis += f"👥 Key Relationships:\n"
            for mem in categories["relationships"]["memories"][:3]:
                analysis += f"  • {mem}\n"
            analysis += "\n"
        
        # Work & Career
        if categories["work"]["memories"]:
            analysis += f"💼 Work & Career:\n"
            for mem in categories["work"]["memories"][:2]:
                analysis += f"  • {mem}\n"
            analysis += "\n"
        
        # Summary insights
        analysis += f"📌 Key Insights:\n"
        analysis += f"  • You have {len(memories)} total memories stored\n"
        
        # Find most common category
        max_category = max(categories.items(), key=lambda x: len(x[1]["memories"]))
        if max_category[1]["memories"]:
            analysis += f"  • Most memories are about: {max_category[0].replace('_', ' ')}\n"
        
        # Recent focus
        recent_memories = memories[-10:] if len(memories) > 10 else memories
        recent_categories = {}
        for memory in recent_memories:
            memory_lower = memory.get('memory', memory.get('text', '')).lower()
            for category, data in categories.items():
                if any(keyword in memory_lower for keyword in data["keywords"]):
                    recent_categories[category] = recent_categories.get(category, 0) + 1
                    break
        
        if recent_categories:
            recent_focus = max(recent_categories.items(), key=lambda x: x[1])
            analysis += f"  • Recent focus: {recent_focus[0].replace('_', ' ')}\n"
        
        return analysis
    except Exception as e:
        return f"Error analyzing memories: {str(e)}"

@mcp.tool(
    description="""Get memories organized by categories. Shows how your memories are distributed across different aspects of your life."""
)
def get_memories_by_category(category: str = None):
    """
    Get memories filtered or grouped by category
    Args:
        category: Specific category to filter by (optional). If not provided, returns all memories grouped by category.
    Returns:
        Memories organized by category
    """
    try:
        # Get all memories with retry logic
        memories = retry_operation(
            lambda: mem0_client.get_all(user_id=DEFAULT_USER_ID),
            max_retries=3,
            retry_delay=1.0
        )
        
        if not memories:
            return "No memories found. Start adding some information for me to remember!"
        
        # Group memories by category
        categorized_memories = {}
        
        for memory in memories:
            memory_text = memory.get('memory', memory.get('text', ''))
            
            # Extract existing tags if any
            tags = []
            if '[#' in memory_text and ']' in memory_text:
                tag_start = memory_text.rfind('[#')
                tag_end = memory_text.rfind(']')
                if tag_start < tag_end:
                    tag_string = memory_text[tag_start+1:tag_end]
                    tags = [tag.strip('#') for tag in tag_string.split() if tag.startswith('#')]
                    memory_text = memory_text[:tag_start].strip()
            
            # If no tags, categorize the memory
            if not tags:
                tags = categorize_memory(memory_text)
            
            # Add to appropriate categories
            for tag in tags:
                if tag not in categorized_memories:
                    categorized_memories[tag] = []
                categorized_memories[tag].append({
                    'content': memory_text,
                    'id': memory.get('id', 'No ID'),
                    'created_at': memory.get('created_at', 'Unknown')
                })
        
        # If specific category requested
        if category:
            if category not in categorized_memories:
                return f"No memories found in category '{category}'. Available categories: {', '.join(sorted(categorized_memories.keys()))}"
            
            memories_in_category = categorized_memories[category]
            output = f"📂 Memories in category '{category}' ({len(memories_in_category)} items):\n"
            output += "=" * 50 + "\n\n"
            
            for i, mem in enumerate(memories_in_category, 1):
                output += f"{i}. [{mem['id']}] {mem['content']}\n"
                output += f"   Created: {mem['created_at']}\n\n"
            
            return output
        
        # Return all memories grouped by category
        output = "📊 Memories by Category\n"
        output += "=" * 50 + "\n\n"
        
        # Sort categories by number of memories
        sorted_categories = sorted(categorized_memories.items(), key=lambda x: len(x[1]), reverse=True)
        
        for cat, mems in sorted_categories:
            cat_name = cat.replace('_', ' ').title()
            output += f"📁 {cat_name} ({len(mems)} memories):\n"
            
            # Show first 3 memories in each category
            for i, mem in enumerate(mems[:3], 1):
                content_preview = mem['content'][:60] + "..." if len(mem['content']) > 60 else mem['content']
                output += f"   {i}. {content_preview}\n"
            
            if len(mems) > 3:
                output += f"   ... and {len(mems) - 3} more\n"
            
            output += "\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Failed to get memories by category: {str(e)}")
        return f"Error getting memories by category: {str(e)}. Please try again later."

@mcp.tool(
    description="""Export all your memories to a JSON file that can be saved or shared. Returns the memories in a structured format."""
)
def export_memories(include_metadata: bool = True):
    """
    Export all memories to JSON format
    Args:
        include_metadata: Whether to include memory IDs and timestamps (default True)
    Returns:
        JSON string of all memories
    """
    try:
        import json
        from datetime import datetime
        
        # Get all memories
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        
        if not memories:
            return json.dumps({
                "user_id": DEFAULT_USER_ID,
                "export_date": datetime.now().isoformat(),
                "total_memories": 0,
                "memories": []
            }, indent=2)
        
        # Prepare export data
        export_data = {
            "user_id": DEFAULT_USER_ID,
            "export_date": datetime.now().isoformat(),
            "total_memories": len(memories),
            "memories": []
        }
        
        # Process each memory
        for memory in memories:
            memory_entry = {
                "content": memory.get('memory', memory.get('text', ''))
            }
            
            if include_metadata:
                memory_entry["id"] = memory.get('id', '')
                memory_entry["created_at"] = memory.get('created_at', '')
                
                # Try to categorize the memory
                memory_lower = memory_entry["content"].lower()
                categories = []
                
                category_keywords = {
                    "personal_info": ["name", "birthday", "age", "live", "from", "born"],
                    "work": ["work", "job", "company", "career", "office", "profession"],
                    "relationships": ["friend", "family", "wife", "husband", "child", "parent", "colleague"],
                    "goals": ["goal", "plan", "want", "wish", "dream", "aspire", "aim"],
                    "knowledge": ["know", "learn", "understand", "fact", "information", "study"],
                    "skills": ["skill", "able", "can", "speak", "language", "expertise"],
                    "dates_events": ["date", "event", "meeting", "appointment", "schedule", "calendar"],
                    "preferences": ["like", "prefer", "favorite", "enjoy", "love", "hate", "dislike"]
                }
                
                for category, keywords in category_keywords.items():
                    if any(keyword in memory_lower for keyword in keywords):
                        categories.append(category)
                
                if categories:
                    memory_entry["categories"] = categories
            
            export_data["memories"].append(memory_entry)
        
        # Return formatted JSON
        json_output = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        return f"Successfully exported {len(memories)} memories:\n\n{json_output}\n\nYou can save this JSON data to a file for backup or sharing."
        
    except Exception as e:
        return f"Error exporting memories: {str(e)}"

@mcp.tool(
    description="""Import memories from a JSON string. This allows you to restore previously exported memories or add memories in bulk. The JSON should have a 'memories' array with objects containing at least a 'content' field."""
)
def import_memories(json_data: str, skip_duplicates: bool = True):
    """
    Import memories from JSON format
    Args:
        json_data: JSON string containing memories to import
        skip_duplicates: Whether to skip memories that might be duplicates (default True)
    Returns:
        Summary of import operation
    """
    try:
        import json
        
        # Parse JSON data
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return f"Invalid JSON format: {str(e)}"
        
        # Validate structure
        if not isinstance(data, dict) or 'memories' not in data:
            return "Invalid format: JSON must contain a 'memories' array"
        
        memories_to_import = data.get('memories', [])
        if not isinstance(memories_to_import, list):
            return "Invalid format: 'memories' must be an array"
        
        # Get existing memories for duplicate checking
        existing_memories = []
        if skip_duplicates:
            existing_memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
            existing_contents = [m.get('memory', m.get('text', '')).lower() for m in existing_memories]
        
        # Import memories
        imported = 0
        skipped = 0
        errors = []
        
        for i, memory in enumerate(memories_to_import):
            try:
                # Extract content
                if isinstance(memory, str):
                    content = memory
                elif isinstance(memory, dict):
                    content = memory.get('content', memory.get('memory', memory.get('text', '')))
                else:
                    errors.append(f"Memory {i+1}: Invalid format")
                    continue
                
                if not content:
                    errors.append(f"Memory {i+1}: Empty content")
                    continue
                
                # Check for duplicates
                if skip_duplicates and content.lower() in existing_contents:
                    skipped += 1
                    continue
                
                # Add the memory
                response = mem0_client.add(content, user_id=DEFAULT_USER_ID)
                if response:
                    imported += 1
                else:
                    errors.append(f"Memory {i+1}: Failed to add")
                    
            except Exception as e:
                errors.append(f"Memory {i+1}: {str(e)}")
        
        # Prepare summary
        summary = f"Import completed:\n"
        summary += f"✅ Successfully imported: {imported} memories\n"
        
        if skipped > 0:
            summary += f"⏭️ Skipped (duplicates): {skipped} memories\n"
        
        if errors:
            summary += f"❌ Errors: {len(errors)} memories\n"
            summary += "Error details:\n"
            for error in errors[:5]:  # Show first 5 errors
                summary += f"  • {error}\n"
            if len(errors) > 5:
                summary += f"  ... and {len(errors) - 5} more errors\n"
        
        return summary
        
    except Exception as e:
        return f"Error importing memories: {str(e)}"

# Create health check endpoint
async def health_check(request: Request):
    return Response(
        content=json.dumps({"status": "healthy", "service": "mem0-mcp"}),
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Create SSE transport handler manually
async def handle_sse(request: Request) -> None:
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
    
    try:
        # Handle both GET and POST for SSE
        async with sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            # Get the internal MCP server and run it
            server = mcp._mcp_server
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f"SSE handler error: {str(e)}")
        # Return empty response for SSE to avoid breaking the connection
        return Response(
            content="",
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )

# Create Starlette app with routes
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["POST", "GET", "OPTIONS"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
        Route("/", endpoint=health_check, methods=["GET"]),
        Route("/health", endpoint=health_check, methods=["GET"])
    ],
    debug=False  # Disable debug mode in production
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MCP Server with Mem0')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8080)), help='Port to bind to')
    
    args = parser.parse_args()
    
    # Configure logging with more detail
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print(f"Starting MCP server with mem0 on {args.host}:{args.port}")
    print(f"SSE endpoint available at http://{args.host}:{args.port}/sse")
    print(f"Health check available at http://{args.host}:{args.port}/health")
    print(f"Messages endpoint available at http://{args.host}:{args.port}/messages/")
    
    # Run with proper configuration
    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port,
        log_level="info",
        access_log=True
    )