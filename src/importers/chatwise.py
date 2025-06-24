"""
Unified Chatwise importer for memory imports
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core import get_client, MemoryCategories

logger = logging.getLogger(__name__)


class ChatwiseImporter:
    """Import memories from Chatwise chat exports"""
    
    def __init__(self):
        self.client = get_client()
        self.categories = MemoryCategories()
    
    def parse_chatwise_export(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a Chatwise export file
        
        Args:
            file_path: Path to the export file
            
        Returns:
            List of parsed memories
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            memories = []
            messages = data.get('messages', [])
            
            for msg in messages:
                # Extract user messages that contain valuable information
                if msg.get('role') == 'user':
                    content = msg.get('content', '').strip()
                    if content and len(content) > 10:  # Skip very short messages
                        memories.append({
                            'content': content,
                            'timestamp': msg.get('timestamp', datetime.now().isoformat()),
                            'metadata': {
                                'source': 'chatwise',
                                'original_id': msg.get('id')
                            }
                        })
            
            return memories
        except Exception as e:
            logger.error(f"Error parsing Chatwise export: {e}")
            raise
    
    def preview(self, file_path: str, limit: int = 10) -> str:
        """
        Preview memories that would be imported
        
        Args:
            file_path: Path to the export file
            limit: Maximum number of memories to preview
            
        Returns:
            Preview summary as string
        """
        try:
            memories = self.parse_chatwise_export(file_path)
            
            preview = f"Found {len(memories)} potential memories to import.\n\n"
            preview += f"Preview (first {min(limit, len(memories))}):\n"
            preview += "-" * 50 + "\n"
            
            for i, memory in enumerate(memories[:limit], 1):
                content = memory['content']
                if len(content) > 100:
                    content = content[:97] + "..."
                
                categories = self.categories.categorize(content)
                preview += f"{i}. {content}\n"
                preview += f"   Categories: {', '.join(categories)}\n\n"
            
            if len(memories) > limit:
                preview += f"... and {len(memories) - limit} more memories\n"
            
            return preview
        except Exception as e:
            return f"Error previewing import: {str(e)}"
    
    def import_single(self, file_path: str, skip_duplicates: bool = True) -> str:
        """
        Import memories from a single file
        
        Args:
            file_path: Path to the export file
            skip_duplicates: Whether to skip duplicate memories
            
        Returns:
            Import summary
        """
        try:
            memories = self.parse_chatwise_export(file_path)
            
            if skip_duplicates:
                # Get existing memories to check for duplicates
                existing = self.client.get_all_memories(page_size=100)
                existing_contents = {m.get('memory', '').lower() for m in existing}
            else:
                existing_contents = set()
            
            imported = 0
            skipped = 0
            errors = []
            
            for memory in memories:
                content = memory['content']
                
                # Check for duplicates
                if content.lower() in existing_contents:
                    skipped += 1
                    continue
                
                try:
                    # Categorize and add memory
                    categories = self.categories.categorize(content)
                    tagged_content = self.categories.format_with_tags(content, categories)
                    
                    metadata = memory.get('metadata', {})
                    metadata['categories'] = categories
                    metadata['imported_at'] = datetime.now().isoformat()
                    
                    self.client.add_memory(tagged_content, metadata=metadata)
                    imported += 1
                    
                    # Add to existing set to avoid importing duplicates within the file
                    existing_contents.add(content.lower())
                    
                except Exception as e:
                    errors.append(f"Failed to import: {content[:50]}... - {str(e)}")
            
            # Generate summary
            summary = f"Import completed:\n"
            summary += f"✅ Imported: {imported} memories\n"
            if skipped > 0:
                summary += f"⏭️  Skipped: {skipped} duplicates\n"
            if errors:
                summary += f"❌ Errors: {len(errors)}\n"
                for error in errors[:5]:
                    summary += f"   - {error}\n"
                if len(errors) > 5:
                    summary += f"   ... and {len(errors) - 5} more errors\n"
            
            return summary
        except Exception as e:
            return f"Error importing memories: {str(e)}"
    
    def import_batch(self, file_paths: List[str], skip_duplicates: bool = True) -> str:
        """
        Import memories from multiple files
        
        Args:
            file_paths: List of paths to export files
            skip_duplicates: Whether to skip duplicate memories
            
        Returns:
            Batch import summary
        """
        total_imported = 0
        total_skipped = 0
        total_errors = 0
        file_summaries = []
        
        for file_path in file_paths:
            try:
                result = self.import_single(file_path, skip_duplicates)
                
                # Parse the result to extract numbers
                lines = result.split('\n')
                for line in lines:
                    if 'Imported:' in line:
                        total_imported += int(line.split(':')[1].split()[0])
                    elif 'Skipped:' in line:
                        total_skipped += int(line.split(':')[1].split()[0])
                    elif 'Errors:' in line:
                        total_errors += int(line.split(':')[1].split()[0])
                
                file_summaries.append(f"✅ {file_path}: Success")
            except Exception as e:
                file_summaries.append(f"❌ {file_path}: {str(e)}")
        
        # Generate batch summary
        summary = f"Batch Import Summary:\n"
        summary += f"Files processed: {len(file_paths)}\n"
        summary += f"Total imported: {total_imported}\n"
        summary += f"Total skipped: {total_skipped}\n"
        summary += f"Total errors: {total_errors}\n\n"
        summary += "File Details:\n"
        for file_summary in file_summaries:
            summary += f"  {file_summary}\n"
        
        return summary
    
    def export_as_json(self, output_path: str, include_metadata: bool = True) -> str:
        """
        Export all memories to JSON format compatible with Chatwise
        
        Args:
            output_path: Path to save the export file
            include_metadata: Whether to include metadata
            
        Returns:
            Export summary
        """
        try:
            memories = self.client.get_all_memories(page_size=100)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_memories": len(memories),
                "format": "chatwise_compatible",
                "memories": []
            }
            
            for memory in memories:
                entry = {
                    "id": memory.get("id"),
                    "content": memory.get("memory", ""),
                    "created_at": memory.get("created_at"),
                    "role": "assistant"  # Mark as assistant memories
                }
                
                if include_metadata:
                    _, tags = self.categories.extract_tags(entry["content"])
                    entry["categories"] = tags
                    entry["metadata"] = memory.get("metadata", {})
                
                export_data["memories"].append(entry)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return f"Successfully exported {len(memories)} memories to {output_path}"
        except Exception as e:
            return f"Error exporting memories: {str(e)}"


# Convenience functions for direct use
def preview_import(file_path: str, limit: int = 10) -> str:
    """Preview memories that would be imported"""
    importer = ChatwiseImporter()
    return importer.preview(file_path, limit)


def import_memories(file_path: str, skip_duplicates: bool = True) -> str:
    """Import memories from a Chatwise export file"""
    importer = ChatwiseImporter()
    return importer.import_single(file_path, skip_duplicates)


def batch_import(file_paths: List[str], skip_duplicates: bool = True) -> str:
    """Import memories from multiple Chatwise export files"""
    importer = ChatwiseImporter()
    return importer.import_batch(file_paths, skip_duplicates)


def export_memories(output_path: str, include_metadata: bool = True) -> str:
    """Export all memories to Chatwise-compatible format"""
    importer = ChatwiseImporter()
    return importer.export_as_json(output_path, include_metadata)