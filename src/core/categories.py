"""
Memory categorization system
"""
from typing import List, Dict, Set
import re


class MemoryCategories:
    """Handles memory categorization and tagging"""
    
    # Category keywords mapping
    CATEGORY_KEYWORDS: Dict[str, List[str]] = {
        "personal_info": [
            "name", "birthday", "age", "live", "from", "born", "address", 
            "phone", "email", "location", "residence", "hometown"
        ],
        "work": [
            "work", "job", "company", "career", "office", "profession", 
            "colleague", "boss", "employee", "business", "occupation", "employer"
        ],
        "relationships": [
            "friend", "family", "wife", "husband", "child", "parent", 
            "sibling", "partner", "mother", "father", "brother", "sister",
            "son", "daughter", "relative"
        ],
        "goals": [
            "goal", "plan", "want", "wish", "dream", "aspire", "aim", 
            "objective", "target", "ambition", "intention", "purpose"
        ],
        "knowledge": [
            "know", "learn", "understand", "fact", "information", "study", 
            "research", "discover", "education", "knowledge", "skill"
        ],
        "skills": [
            "skill", "able", "can", "speak", "language", "expertise", 
            "proficient", "experienced", "capability", "competence"
        ],
        "dates_events": [
            "date", "event", "meeting", "appointment", "schedule", "calendar", 
            "tomorrow", "yesterday", "today", "week", "month", "year",
            "deadline", "anniversary"
        ],
        "preferences": [
            "like", "prefer", "favorite", "enjoy", "love", "hate", "dislike", 
            "interest", "hobby", "passion", "taste"
        ],
        "health": [
            "health", "medical", "doctor", "medicine", "sick", "exercise", 
            "diet", "sleep", "illness", "condition", "treatment", "wellness"
        ],
        "hobbies": [
            "hobby", "fun", "play", "game", "sport", "music", "art", 
            "travel", "read", "watch", "leisure", "entertainment"
        ],
        "technical": [
            "code", "programming", "software", "hardware", "technology",
            "computer", "system", "database", "network", "algorithm"
        ],
        "finance": [
            "money", "budget", "expense", "income", "save", "invest",
            "loan", "credit", "debt", "financial", "bank", "payment"
        ]
    }
    
    # Common words to ignore when categorizing
    STOP_WORDS: Set[str] = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "about", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "under", "again",
        "further", "then", "once", "is", "am", "are", "was", "were", "be",
        "have", "has", "had", "do", "does", "did", "will", "would", "should",
        "could", "may", "might", "must", "can", "shall"
    }
    
    @classmethod
    def categorize(cls, content: str) -> List[str]:
        """
        Categorize memory content based on keywords
        
        Args:
            content: The memory content to categorize
            
        Returns:
            List of applicable categories
        """
        # Normalize content
        content_lower = content.lower()
        
        # Remove punctuation for better matching
        content_normalized = re.sub(r'[^\w\s]', ' ', content_lower)
        
        # Split into words and filter stop words
        words = [w for w in content_normalized.split() if w not in cls.STOP_WORDS]
        
        categories = []
        scores = {}
        
        # Calculate scores for each category
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Check for exact word match
                if keyword in words:
                    score += 2
                # Check for partial match in original content
                elif keyword in content_lower:
                    score += 1
            
            if score > 0:
                scores[category] = score
        
        # Sort categories by score and take top matches
        if scores:
            sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            # Take categories with significant scores
            threshold = max(scores.values()) * 0.5
            categories = [cat for cat, score in sorted_categories if score >= threshold]
        
        # If no category matches, mark as "other"
        if not categories:
            categories.append("other")
        
        return categories[:3]  # Return top 3 categories max
    
    @classmethod
    def format_with_tags(cls, content: str, categories: List[str]) -> str:
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
    
    @classmethod
    def extract_tags(cls, content: str) -> tuple[str, List[str]]:
        """
        Extract content and tags from a tagged memory string
        
        Args:
            content: Memory string potentially with tags
            
        Returns:
            Tuple of (clean content, list of tags)
        """
        # Pattern to match tags at the end [#tag1 #tag2]
        pattern = r'\[(#\w+(?:\s+#\w+)*)\]$'
        match = re.search(pattern, content)
        
        if match:
            # Extract clean content
            clean_content = content[:match.start()].strip()
            # Extract tags
            tags_str = match.group(1)
            tags = [tag.strip('#') for tag in tags_str.split()]
            return clean_content, tags
        
        return content, []
    
    @classmethod
    def get_category_description(cls, category: str) -> str:
        """
        Get a human-readable description of a category
        
        Args:
            category: Category name
            
        Returns:
            Description string
        """
        descriptions = {
            "personal_info": "Personal information and identity",
            "work": "Work and career related",
            "relationships": "Family, friends, and relationships",
            "goals": "Goals, plans, and aspirations",
            "knowledge": "Knowledge and learning",
            "skills": "Skills and capabilities",
            "dates_events": "Important dates and events",
            "preferences": "Preferences and interests",
            "health": "Health and wellness",
            "hobbies": "Hobbies and entertainment",
            "technical": "Technical and programming",
            "finance": "Financial matters",
            "other": "Uncategorized"
        }
        return descriptions.get(category, "Unknown category")
    
    @classmethod
    def suggest_category(cls, query: str) -> List[str]:
        """
        Suggest categories based on a search query
        
        Args:
            query: Search query
            
        Returns:
            List of suggested categories
        """
        query_lower = query.lower()
        suggestions = []
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            if any(keyword in query_lower for keyword in keywords):
                suggestions.append(category)
        
        return suggestions[:2]  # Return top 2 suggestions