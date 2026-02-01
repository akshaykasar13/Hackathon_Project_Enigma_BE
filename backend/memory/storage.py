"""
Memory storage with persistence.
Manages Working, Episodic, and Semantic memory types.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from backend import config

MEMORY_DIR = config.MEMORY_DIR
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


class JSONMemoryStorage:
    """JSON-based memory storage (original implementation)."""
    
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


# Try to import mem0 (optional)
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("[MemoryStorage] mem0 not available, will use JSON fallback")


class Mem0MemoryStorage:
    """Mem0-based memory storage with semantic search capabilities."""
    
    def __init__(self):
        """Initialize mem0 with OpenAI embeddings."""
        if not MEM0_AVAILABLE:
            raise ImportError("mem0 is not installed. Install with: pip install mem0ai")
        
        if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "test-key-not-used":
            raise ValueError("OpenAI API key required for mem0. Set OPENAI_API_KEY in .env")
        
        try:
            # Initialize mem0 with optimized configuration
            # Fine-tuned for support/incident use case
            mem0_config = {
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "agent_memories",
                        "path": str(config.PROJECT_ROOT / "data" / "mem0_db")
                    }
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small"  # Fast and cost-effective
                    }
                },
                # Memory management settings
                "memory_store": {
                    "provider": "local",
                    "config": {
                        "path": str(config.PROJECT_ROOT / "data" / "mem0_store")
                    }
                }
            }
            
            # Allow custom mem0 config via environment variable (optional)
            mem0_custom_config = os.getenv("MEM0_CUSTOM_CONFIG")
            if mem0_custom_config:
                try:
                    import json
                    custom_config = json.loads(mem0_custom_config)
                    mem0_config.update(custom_config)
                    print("[Mem0MemoryStorage] Using custom configuration from MEM0_CUSTOM_CONFIG")
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Failed to parse custom config: {e}, using default")
            
            self.memory = Memory.from_config(mem0_config)
            
            # Track memory IDs for our three memory types
            # We'll use mem0's user_id to separate memory types
            self._working_memory_user_prefix = "working_"
            self._episodic_memory_user_prefix = "episodic_"
            self._semantic_memory_user_prefix = "semantic_"
            
            print("[Mem0MemoryStorage] Initialized successfully with OpenAI embeddings")
        except Exception as e:
            print(f"[Mem0MemoryStorage] Initialization failed: {e}")
            raise
    
    # Working Memory - Task-level, short-lived context
    def add_working_memory(self, task_id: str, context: Dict[str, Any]):
        """Add to working memory (current task context)."""
        user_id = f"{self._working_memory_user_prefix}{task_id}"
        memory_text = f"Task context: {json.dumps(context, default=str)}"
        
        try:
            self.memory.add(
                messages=[{"role": "user", "content": memory_text}],
                user_id=user_id,
                metadata={"type": "working_memory", "task_id": task_id, "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error adding working memory: {e}")
            raise
    
    def get_working_memory(self, task_id: str = None) -> List[Dict]:
        """Get working memory for task or all."""
        try:
            if task_id:
                user_id = f"{self._working_memory_user_prefix}{task_id}"
                # mem0.search() requires a query - use a broad query to get all memories for this user
                memories = self.memory.search(query="task context", user_id=user_id, limit=config.MEM0_SEARCH_LIMIT)
                # Convert mem0 format to our expected format
                result = []
                for m in memories:
                    # Handle both dict and string responses
                    if isinstance(m, str):
                        continue  # Skip string responses
                    if not isinstance(m, dict):
                        continue
                    try:
                        meta = m.get("metadata", {})
                        if not isinstance(meta, dict):
                            meta = {}
                        memory_content = m.get("memory", "{}")
                        if isinstance(memory_content, str):
                            try:
                                context = json.loads(memory_content)
                            except:
                                context = {"content": memory_content}
                        else:
                            context = memory_content
                        result.append({
                            "task_id": task_id,
                            "timestamp": meta.get("timestamp", ""),
                            "context": context
                        })
                    except Exception as e:
                        print(f"[Mem0MemoryStorage] Error parsing memory: {e}")
                        continue
                return result
            else:
                # Get all working memories (this is less efficient, but maintains compatibility)
                # For now, return empty - working memory is typically task-specific
                return []
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error getting working memory: {e}")
            return []
    
    def clear_working_memory(self, task_id: str = None):
        """Clear working memory."""
        # mem0 doesn't have a direct "clear" - we'd need to delete specific memories
        # For now, this is a no-op (mem0 manages memory automatically)
        pass
    
    # Episodic Memory - Past incidents, conversations, outcomes
    def add_episodic_memory(self, incident: str, outcome: str = None, metadata: Dict = None):
        """Add episodic memory (past incidents/conversations)."""
        user_id = self._episodic_memory_user_prefix + "default"
        memory_text = f"Incident: {incident}"
        if outcome:
            memory_text += f"\nOutcome: {outcome}"
        
        try:
            result = self.memory.add(
                messages=[{"role": "user", "content": memory_text}],
                user_id=user_id,
                metadata={
                    "type": "episodic_memory",
                    "incident": incident,
                    "outcome": outcome,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            # mem0 returns memory IDs - we'll need to track them
            # For now, return a hash-based ID for compatibility
            import hashlib
            memory_id = int(hashlib.md5(memory_text.encode()).hexdigest()[:8], 16) % 1000000
            return memory_id
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error adding episodic memory: {e}")
            raise
    
    def get_episodic_memory(self, limit: int = None) -> List[Dict]:
        """Get episodic memories."""
        try:
            user_id = self._episodic_memory_user_prefix + "default"
            # Use provided limit or config default, but cap at reasonable max
            search_limit = limit if limit else config.MEM0_SEARCH_LIMIT * 10  # Allow more for get operations
            # mem0.search() requires a query - use multiple broad queries to get all episodic memories
            # Try different queries to catch all memories
            all_memories = []
            queries = ["incident", "ticket", "issue", "problem", "error", "support", "request"]
            seen_ids = set()
            
            for query in queries:
                try:
                    memories = self.memory.search(query=query, user_id=user_id, limit=min(search_limit, 1000))
                    for m in memories:
                        # Use memory content as unique identifier to avoid duplicates
                        if isinstance(m, dict):
                            mem_id = str(m.get("memory", "")) + str(m.get("metadata", {}).get("timestamp", ""))
                            if mem_id not in seen_ids:
                                seen_ids.add(mem_id)
                                all_memories.append(m)
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Search with query '{query}' failed: {e}")
                    continue
            
            # If still no results, try with a very generic query
            if not all_memories:
                try:
                    memories = self.memory.search(query="memory", user_id=user_id, limit=min(search_limit, 1000))
                    all_memories = list(memories) if memories else []
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Generic search failed: {e}")
            
            memories = all_memories[:min(search_limit, 1000)]  # Limit results
            # Convert to our format
            result = []
            for idx, m in enumerate(memories, 1):
                # Handle both dict and string responses
                if isinstance(m, str):
                    continue  # Skip string responses
                if not isinstance(m, dict):
                    continue
                try:
                    meta = m.get("metadata", {})
                    if not isinstance(meta, dict):
                        meta = {}
                    result.append({
                        "id": idx,  # Sequential ID for compatibility
                        "incident": meta.get("incident", ""),
                        "outcome": meta.get("outcome", ""),
                        "timestamp": meta.get("timestamp", ""),
                        "metadata": {k: v for k, v in meta.items() if k not in ["incident", "outcome", "timestamp", "type"]}
                    })
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Error parsing episodic memory: {e}")
                    continue
            return result
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error getting episodic memory: {e}")
            return []
    
    def search_episodic_memory(self, query: str) -> List[Dict]:
        """Search episodic memory by query - NOW WITH SEMANTIC SEARCH!"""
        try:
            user_id = self._episodic_memory_user_prefix + "default"
            # mem0's search is semantic by default!
            # Use configurable limit for better performance
            memories = self.memory.search(query=query, user_id=user_id, limit=config.MEM0_SEARCH_LIMIT)
            # Convert to our format
            result = []
            for idx, m in enumerate(memories, 1):
                # Handle both dict and string responses
                if isinstance(m, str):
                    continue  # Skip string responses
                if not isinstance(m, dict):
                    continue
                try:
                    meta = m.get("metadata", {})
                    if not isinstance(meta, dict):
                        meta = {}
                    result.append({
                        "id": idx,
                        "incident": meta.get("incident", ""),
                        "outcome": meta.get("outcome", ""),
                        "timestamp": meta.get("timestamp", ""),
                        "metadata": {k: v for k, v in meta.items() if k not in ["incident", "outcome", "timestamp", "type"]}
                    })
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Error parsing episodic search result: {e}")
                    continue
            return result
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error searching episodic memory: {e}")
            return []
    
    def delete_episodic_memory(self, memory_id: int):
        """Delete episodic memory by ID."""
        # mem0 doesn't have direct ID-based deletion in the same way
        # This would require tracking mem0's internal IDs
        # For now, this is a no-op (can be implemented later)
        pass
    
    def update_episodic_memory(self, memory_id: int, updates: Dict):
        """Update episodic memory."""
        # mem0 doesn't have direct update - would need to delete and re-add
        # For now, return False (can be implemented later)
        return False
    
    # Semantic Memory - Documents, FAQs, runbooks
    def add_semantic_memory(self, content: str, doc_type: str = "document", metadata: Dict = None):
        """Add semantic memory (documents, FAQs, runbooks)."""
        user_id = f"{self._semantic_memory_user_prefix}{doc_type}"
        
        try:
            result = self.memory.add(
                messages=[{"role": "user", "content": content}],
                user_id=user_id,
                metadata={
                    "type": "semantic_memory",
                    "doc_type": doc_type,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            # Return hash-based ID for compatibility
            import hashlib
            memory_id = int(hashlib.md5(content.encode()).hexdigest()[:8], 16) % 1000000
            return memory_id
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error adding semantic memory: {e}")
            raise
    
    def get_semantic_memory(self, doc_type: str = None) -> List[Dict]:
        """Get semantic memories."""
        try:
            if doc_type:
                user_id = f"{self._semantic_memory_user_prefix}{doc_type}"
            else:
                # Get all semantic memories (less efficient)
                user_id = self._semantic_memory_user_prefix + "document"  # Default
            # Use configurable limit, but allow more for get operations
            # mem0.search() requires a query - use multiple broad queries to get all semantic memories
            all_memories = []
            queries = ["document", "content", "information", "knowledge", "data", "text", "memory"]
            seen_ids = set()
            
            for query in queries:
                try:
                    memories = self.memory.search(query=query, user_id=user_id, limit=config.MEM0_SEARCH_LIMIT * 10)
                    for m in memories:
                        # Use memory content as unique identifier to avoid duplicates
                        if isinstance(m, dict):
                            mem_id = str(m.get("memory", "")) + str(m.get("metadata", {}).get("timestamp", ""))
                            if mem_id not in seen_ids:
                                seen_ids.add(mem_id)
                                all_memories.append(m)
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Search with query '{query}' failed: {e}")
                    continue
            
            # If still no results, try with a very generic query
            if not all_memories:
                try:
                    memories = self.memory.search(query="semantic", user_id=user_id, limit=config.MEM0_SEARCH_LIMIT * 10)
                    all_memories = list(memories) if memories else []
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Generic search failed: {e}")
            
            memories = all_memories[:config.MEM0_SEARCH_LIMIT * 10]  # Limit results
            result = []
            for idx, m in enumerate(memories, 1):
                # Handle both dict and string responses
                if isinstance(m, str):
                    continue  # Skip string responses
                if not isinstance(m, dict):
                    continue
                try:
                    meta = m.get("metadata", {})
                    if not isinstance(meta, dict):
                        meta = {}
                    result.append({
                        "id": idx,
                        "content": m.get("memory", ""),
                        "doc_type": meta.get("doc_type", "document"),
                        "timestamp": meta.get("timestamp", ""),
                        "metadata": {k: v for k, v in meta.items() if k not in ["doc_type", "timestamp", "type"]}
                    })
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Error parsing semantic memory: {e}")
                    continue
            return result
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error getting semantic memory: {e}")
            return []
    
    def search_semantic_memory(self, query: str) -> List[Dict]:
        """Search semantic memory by query - NOW WITH SEMANTIC SEARCH!"""
        try:
            # Search across all semantic memory types
            user_id = self._semantic_memory_user_prefix + "document"  # Default
            # Use configurable limit for better performance
            memories = self.memory.search(query=query, user_id=user_id, limit=config.MEM0_SEARCH_LIMIT)
            result = []
            for idx, m in enumerate(memories, 1):
                # Handle both dict and string responses
                if isinstance(m, str):
                    continue  # Skip string responses
                if not isinstance(m, dict):
                    continue
                try:
                    meta = m.get("metadata", {})
                    if not isinstance(meta, dict):
                        meta = {}
                    result.append({
                        "id": idx,
                        "content": m.get("memory", ""),
                        "doc_type": meta.get("doc_type", "document"),
                        "timestamp": meta.get("timestamp", ""),
                        "metadata": {k: v for k, v in meta.items() if k not in ["doc_type", "timestamp", "type"]}
                    })
                except Exception as e:
                    print(f"[Mem0MemoryStorage] Error parsing semantic search result: {e}")
                    continue
            return result
        except Exception as e:
            print(f"[Mem0MemoryStorage] Error searching semantic memory: {e}")
            return []
    
    def delete_semantic_memory(self, memory_id: int):
        """Delete semantic memory by ID."""
        # Similar to episodic - would need mem0 internal ID tracking
        pass
    
    def update_semantic_memory(self, memory_id: int, updates: Dict):
        """Update semantic memory."""
        return False


# Main MemoryStorage class with smart wrapper and fallback
class MemoryStorage:
    """Main memory storage class with mem0 integration and JSON fallback."""
    
    def __init__(self):
        """Initialize with mem0 if enabled and available, otherwise use JSON."""
        self._using_mem0 = False
        self._json_fallback = JSONMemoryStorage()  # Always keep JSON as fallback
        
        # Try to use mem0 if enabled
        if config.USE_MEM0 and MEM0_AVAILABLE:
            try:
                if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "test-key-not-used":
                    print("[MemoryStorage] mem0 requires OpenAI API key - using JSON fallback")
                    self._impl = self._json_fallback
                else:
                    self._impl = Mem0MemoryStorage()
                    self._using_mem0 = True
                    print("[MemoryStorage] [OK] Using mem0 with semantic search capabilities")
            except Exception as e:
                print(f"[MemoryStorage] [WARNING] mem0 initialization failed: {e}")
                if config.MEM0_FALLBACK_TO_JSON:
                    print("[MemoryStorage] Falling back to JSON storage")
                    self._impl = self._json_fallback
                else:
                    raise
        else:
            # Use JSON storage
            self._impl = self._json_fallback
            if config.USE_MEM0 and not MEM0_AVAILABLE:
                print("[MemoryStorage] mem0 not installed - using JSON storage")
            else:
                print("[MemoryStorage] Using JSON storage (USE_MEM0=false)")
    
    def _safe_call(self, method_name: str, *args, **kwargs):
        """Safely call method with fallback to JSON if mem0 fails."""
        if not self._using_mem0:
            # Not using mem0, just call directly
            method = getattr(self._impl, method_name)
            return method(*args, **kwargs)
        
        # Using mem0 - try with fallback
        try:
            method = getattr(self._impl, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            if config.MEM0_FALLBACK_TO_JSON:
                print(f"[MemoryStorage] ⚠️  mem0.{method_name} failed: {e}, falling back to JSON")
                # Fallback to JSON
                method = getattr(self._json_fallback, method_name)
                return method(*args, **kwargs)
            else:
                raise
    
    # Delegate all methods with safe fallback
    def add_working_memory(self, task_id: str, context: Dict[str, Any]):
        return self._safe_call("add_working_memory", task_id, context)
    
    def get_working_memory(self, task_id: str = None) -> List[Dict]:
        return self._safe_call("get_working_memory", task_id)
    
    def clear_working_memory(self, task_id: str = None):
        return self._safe_call("clear_working_memory", task_id)
    
    def add_episodic_memory(self, incident: str, outcome: str = None, metadata: Dict = None):
        return self._safe_call("add_episodic_memory", incident, outcome, metadata)
    
    def get_episodic_memory(self, limit: int = None) -> List[Dict]:
        return self._safe_call("get_episodic_memory", limit)
    
    def search_episodic_memory(self, query: str) -> List[Dict]:
        return self._safe_call("search_episodic_memory", query)
    
    def delete_episodic_memory(self, memory_id: int):
        return self._safe_call("delete_episodic_memory", memory_id)
    
    def update_episodic_memory(self, memory_id: int, updates: Dict):
        return self._safe_call("update_episodic_memory", memory_id, updates)
    
    def add_semantic_memory(self, content: str, doc_type: str = "document", metadata: Dict = None):
        return self._safe_call("add_semantic_memory", content, doc_type, metadata)
    
    def get_semantic_memory(self, doc_type: str = None) -> List[Dict]:
        return self._safe_call("get_semantic_memory", doc_type)
    
    def search_semantic_memory(self, query: str) -> List[Dict]:
        return self._safe_call("search_semantic_memory", query)
    
    def delete_semantic_memory(self, memory_id: int):
        return self._safe_call("delete_semantic_memory", memory_id)
    
    def update_semantic_memory(self, memory_id: int, updates: Dict):
        return self._safe_call("update_semantic_memory", memory_id, updates)


# Global memory storage instance
memory_storage = MemoryStorage()

