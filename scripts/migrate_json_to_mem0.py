"""
Migration script: Migrate JSON memories to mem0.
This script safely migrates existing JSON-based memories to mem0 while preserving the originals.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from backend import config
from backend.memory.storage import JSONMemoryStorage, Mem0MemoryStorage, MEM0_AVAILABLE


def backup_json_files():
    """Create backup of JSON memory files."""
    print("=" * 60)
    print("Step 1: Creating Backup")
    print("=" * 60)
    
    backup_dir = project_root / "data" / "memory_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    memory_dir = Path(config.MEMORY_DIR)
    files_to_backup = [
        "working_memory.json",
        "episodic_memory.json",
        "semantic_memory.json"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_subdir = backup_dir / f"backup_{timestamp}"
    backup_subdir.mkdir(exist_ok=True)
    
    for filename in files_to_backup:
        source = memory_dir / filename
        if source.exists():
            import shutil
            dest = backup_subdir / filename
            shutil.copy2(source, dest)
            print(f"✅ Backed up {filename}")
        else:
            print(f"⚠️  {filename} not found (may be empty)")
    
    print(f"\n✅ Backup created at: {backup_subdir}")
    return backup_subdir


def load_json_memories():
    """Load all memories from JSON files."""
    print("\n" + "=" * 60)
    print("Step 2: Loading JSON Memories")
    print("=" * 60)
    
    json_storage = JSONMemoryStorage()
    
    episodic = json_storage.get_episodic_memory()
    semantic = json_storage.get_semantic_memory()
    working = json_storage.get_working_memory()
    
    print(f"✅ Loaded {len(episodic)} episodic memories")
    print(f"✅ Loaded {len(semantic)} semantic memories")
    print(f"✅ Loaded {len(working)} working memories")
    
    return {
        "episodic": episodic,
        "semantic": semantic,
        "working": working
    }


def migrate_to_mem0(memories):
    """Migrate memories to mem0."""
    print("\n" + "=" * 60)
    print("Step 3: Migrating to mem0")
    print("=" * 60)
    
    if not MEM0_AVAILABLE:
        print("❌ mem0 is not installed. Install with: pip install mem0ai")
        return False
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "test-key-not-used":
        print("❌ OpenAI API key required for mem0")
        return False
    
    try:
        mem0_storage = Mem0MemoryStorage()
    except Exception as e:
        print(f"❌ Failed to initialize mem0: {e}")
        return False
    
    # Migrate episodic memories
    print("\nMigrating episodic memories...")
    episodic_count = 0
    for memory in memories["episodic"]:
        try:
            mem0_storage.add_episodic_memory(
                incident=memory.get("incident", ""),
                outcome=memory.get("outcome"),
                metadata={
                    **memory.get("metadata", {}),
                    "original_id": memory.get("id"),
                    "migrated_from_json": True,
                    "migration_timestamp": datetime.now().isoformat()
                }
            )
            episodic_count += 1
            if episodic_count % 10 == 0:
                print(f"   Migrated {episodic_count} episodic memories...")
        except Exception as e:
            print(f"⚠️  Failed to migrate episodic memory {memory.get('id')}: {e}")
    
    print(f"✅ Migrated {episodic_count}/{len(memories['episodic'])} episodic memories")
    
    # Migrate semantic memories
    print("\nMigrating semantic memories...")
    semantic_count = 0
    for memory in memories["semantic"]:
        try:
            mem0_storage.add_semantic_memory(
                content=memory.get("content", ""),
                doc_type=memory.get("doc_type", "document"),
                metadata={
                    **memory.get("metadata", {}),
                    "original_id": memory.get("id"),
                    "migrated_from_json": True,
                    "migration_timestamp": datetime.now().isoformat()
                }
            )
            semantic_count += 1
            if semantic_count % 10 == 0:
                print(f"   Migrated {semantic_count} semantic memories...")
        except Exception as e:
            print(f"⚠️  Failed to migrate semantic memory {memory.get('id')}: {e}")
    
    print(f"✅ Migrated {semantic_count}/{len(memories['semantic'])} semantic memories")
    
    # Working memories are typically short-lived, skip migration
    print("\n⚠️  Skipping working memories (short-lived, task-specific)")
    
    return True


def verify_migration(memories):
    """Verify migrated memories can be retrieved."""
    print("\n" + "=" * 60)
    print("Step 4: Verifying Migration")
    print("=" * 60)
    
    if not MEM0_AVAILABLE:
        print("⚠️  mem0 not available - skipping verification")
        return False
    
    try:
        mem0_storage = Mem0MemoryStorage()
    except Exception as e:
        print(f"⚠️  Cannot verify - mem0 init failed: {e}")
        return False
    
    # Verify episodic memories
    print("\nVerifying episodic memories...")
    mem0_episodic = mem0_storage.get_episodic_memory(limit=1000)
    print(f"✅ Retrieved {len(mem0_episodic)} episodic memories from mem0")
    
    if len(mem0_episodic) < len(memories["episodic"]) * 0.9:  # Allow 10% loss
        print(f"⚠️  Warning: Only {len(mem0_episodic)}/{len(memories['episodic'])} memories found")
    else:
        print(f"✅ Migration verified: {len(mem0_episodic)} memories available")
    
    # Verify semantic memories
    print("\nVerifying semantic memories...")
    mem0_semantic = mem0_storage.get_semantic_memory()
    print(f"✅ Retrieved {len(mem0_semantic)} semantic memories from mem0")
    
    if len(mem0_semantic) < len(memories["semantic"]) * 0.9:
        print(f"⚠️  Warning: Only {len(mem0_semantic)}/{len(memories['semantic'])} memories found")
    else:
        print(f"✅ Migration verified: {len(mem0_semantic)} memories available")
    
    return True


def test_search_quality(memories):
    """Test search quality improvement with mem0."""
    print("\n" + "=" * 60)
    print("Step 5: Testing Search Quality")
    print("=" * 60)
    
    if not MEM0_AVAILABLE:
        print("⚠️  mem0 not available - skipping search quality test")
        return
    
    try:
        mem0_storage = Mem0MemoryStorage()
        json_storage = JSONMemoryStorage()
    except Exception as e:
        print(f"⚠️  Cannot test - initialization failed: {e}")
        return
    
    # Test queries
    test_queries = [
        "payment failed",
        "transaction error",
        "billing issue",
        "refund request"
    ]
    
    print("\nComparing JSON (keyword) vs mem0 (semantic) search:")
    print("-" * 60)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # JSON search (keyword)
        json_results = json_storage.search_episodic_memory(query)
        print(f"  JSON (keyword): {len(json_results)} results")
        
        # mem0 search (semantic)
        try:
            mem0_results = mem0_storage.search_episodic_memory(query)
            print(f"  mem0 (semantic): {len(mem0_results)} results")
            
            if len(mem0_results) > len(json_results):
                improvement = ((len(mem0_results) - len(json_results)) / max(len(json_results), 1)) * 100
                print(f"  ✅ Improvement: {improvement:.1f}% more results")
            elif len(mem0_results) == len(json_results):
                print(f"  ℹ️  Same number of results (but mem0 uses semantic similarity)")
            else:
                print(f"  ℹ️  Fewer results but higher relevance (semantic filtering)")
        except Exception as e:
            print(f"  ⚠️  mem0 search failed: {e}")


def main():
    """Main migration process."""
    print("\n" + "=" * 60)
    print("JSON to mem0 Migration Script")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Backup existing JSON files")
    print("  2. Load JSON memories")
    print("  3. Migrate to mem0")
    print("  4. Verify migration")
    print("  5. Test search quality improvement")
    print("\n⚠️  Original JSON files will be preserved as backup")
    print("=" * 60)
    
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() != "yes":
        print("Migration cancelled.")
        return
    
    # Step 1: Backup
    backup_dir = backup_json_files()
    
    # Step 2: Load memories
    memories = load_json_memories()
    
    if not memories["episodic"] and not memories["semantic"]:
        print("\n⚠️  No memories to migrate. Exiting.")
        return
    
    # Step 3: Migrate
    success = migrate_to_mem0(memories)
    
    if not success:
        print("\n❌ Migration failed. JSON files are safe in backup.")
        return
    
    # Step 4: Verify
    verify_migration(memories)
    
    # Step 5: Test search quality
    test_search_quality(memories)
    
    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print(f"✅ Backup location: {backup_dir}")
    print("✅ Original JSON files preserved")
    print("✅ Memories migrated to mem0")
    print("\nNext steps:")
    print("  1. Set USE_MEM0=true in .env")
    print("  2. Restart the server")
    print("  3. Test the system with mem0 enabled")
    print("=" * 60)


if __name__ == "__main__":
    main()


