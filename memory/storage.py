"""
Memory storage with persistence.
Manages Working, Episodic, and Semantic memory types.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any

MEMORY_DIR = "backend/data/memory"
WORKING_MEMORY_FILE = os.path.join(MEMORY_DIR, "working_memory.json")
EPISODIC_MEMORY_FILE = os.path.join(MEMORY_DIR, "episodic_memory.json")
SEMANTIC_MEMORY_FILE = os.path.join(MEMORY_DIR, "semantic_memory.json")

# Ensure memory directory exists
os.makedirs(MEMORY_DIR, exist_ok=True)


def load_json_file(filepath: str, default: Any = None) -> Any:
    """Load JSON file, return default if doesn't exist."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default if default is not None else []
    except (json.JSONDecodeError, IOError) as e:
        print(f"[MemoryStorage] Error loading {filepath}: {e}")
        return default if default is not None else []


def save_json_file(filepath: str, data: Any):
    """Save data to JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except (IOError, OSError) as e:
        print(f"[MemoryStorage] Error saving {filepath}: {e}")
        raise


class MemoryStorage:
    """Manages three types of memory with persistence."""
    
    def __init__(self):
        self.working_memory = load_json_file(WORKING_MEMORY_FILE, [])
        self.episodic_memory = load_json_file(EPISODIC_MEMORY_FILE, [])
        self.semantic_memory = load_json_file(SEMANTIC_MEMORY_FILE, [])
    
    # Working Memory - Task-level, short-lived context
    def add_working_memory(self, task_id: str, context: Dict[str, Any]):
        """Add to working memory (current task context)."""
        entry = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        self.working_memory.append(entry)
        # Keep only last 10 working memory entries
        if len(self.working_memory) > 10:
            self.working_memory = self.working_memory[-10:]
        save_json_file(WORKING_MEMORY_FILE, self.working_memory)
    
    def get_working_memory(self, task_id: str = None) -> List[Dict]:
        """Get working memory for task or all."""
        if task_id:
            return [m for m in self.working_memory if m.get("task_id") == task_id]
        return self.working_memory
    
    def clear_working_memory(self, task_id: str = None):
        """Clear working memory."""
        if task_id:
            self.working_memory = [m for m in self.working_memory if m.get("task_id") != task_id]
        else:
            self.working_memory = []
        save_json_file(WORKING_MEMORY_FILE, self.working_memory)
    
    # Episodic Memory - Past incidents, conversations, outcomes
    def add_episodic_memory(self, incident: str, outcome: str = None, metadata: Dict = None):
        """Add episodic memory (past incidents/conversations)."""
        entry = {
            "id": len(self.episodic_memory) + 1,
            "incident": incident,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.episodic_memory.append(entry)
        save_json_file(EPISODIC_MEMORY_FILE, self.episodic_memory)
        return entry["id"]
    
    def get_episodic_memory(self, limit: int = None) -> List[Dict]:
        """Get episodic memories."""
        memories = self.episodic_memory
        if limit:
            memories = memories[-limit:]
        return memories
    
    def search_episodic_memory(self, query: str) -> List[Dict]:
        """Search episodic memory by query."""
        query_lower = query.lower()
        return [
            m for m in self.episodic_memory
            if query_lower in m.get("incident", "").lower() or
               query_lower in m.get("outcome", "").lower()
        ]
    
    def delete_episodic_memory(self, memory_id: int):
        """Delete episodic memory by ID."""
        self.episodic_memory = [m for m in self.episodic_memory if m.get("id") != memory_id]
        save_json_file(EPISODIC_MEMORY_FILE, self.episodic_memory)
    
    def update_episodic_memory(self, memory_id: int, updates: Dict):
        """Update episodic memory."""
        for memory in self.episodic_memory:
            if memory.get("id") == memory_id:
                memory.update(updates)
                save_json_file(EPISODIC_MEMORY_FILE, self.episodic_memory)
                return True
        return False
    
    # Semantic Memory - Documents, FAQs, runbooks
    def add_semantic_memory(self, content: str, doc_type: str = "document", metadata: Dict = None):
        """Add semantic memory (documents, FAQs, runbooks)."""
        entry = {
            "id": len(self.semantic_memory) + 1,
            "content": content,
            "doc_type": doc_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.semantic_memory.append(entry)
        save_json_file(SEMANTIC_MEMORY_FILE, self.semantic_memory)
        return entry["id"]
    
    def get_semantic_memory(self, doc_type: str = None) -> List[Dict]:
        """Get semantic memories."""
        if doc_type:
            return [m for m in self.semantic_memory if m.get("doc_type") == doc_type]
        return self.semantic_memory
    
    def search_semantic_memory(self, query: str) -> List[Dict]:
        """Search semantic memory by query."""
        query_lower = query.lower()
        return [
            m for m in self.semantic_memory
            if query_lower in m.get("content", "").lower()
        ]
    
    def delete_semantic_memory(self, memory_id: int):
        """Delete semantic memory by ID."""
        self.semantic_memory = [m for m in self.semantic_memory if m.get("id") != memory_id]
        save_json_file(SEMANTIC_MEMORY_FILE, self.semantic_memory)
    
    def update_semantic_memory(self, memory_id: int, updates: Dict):
        """Update semantic memory."""
        for memory in self.semantic_memory:
            if memory.get("id") == memory_id:
                memory.update(updates)
                save_json_file(SEMANTIC_MEMORY_FILE, self.semantic_memory)
                return True
        return False


# Global memory storage instance
memory_storage = MemoryStorage()

