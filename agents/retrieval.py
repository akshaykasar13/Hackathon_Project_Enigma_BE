"""
Retrieval agent for retrieving relevant information.
"""
from backend.rag.vector_store import db
from backend.observability import observability

def retrieve(state):
    """Retrieve relevant information."""
    query = state.get("ticket", "")
    tool_call = observability.log_tool_call("document_retrieval", "RetrievalAgent", {"query": query[:100]})
    
    try:
        if not query:
            print("[RetrievalAgent] No query provided, skipping retrieval")
            state["retrieved_docs"] = []
            state["context"] = state.get("context", [])
            observability.log_tool_result(tool_call, {"docs_retrieved": 0, "reason": "no_query"})
            return state
        
        docs = db.similarity_search(query, k=3)
        state["retrieved_docs"] = [d.page_content for d in docs]
        # Also add to context for reasoning
        if "context" not in state:
            state["context"] = []
        state["context"].extend([d.page_content[:100] + "..." for d in docs])  # Truncate for display
        
        observability.log_tool_result(tool_call, {"docs_retrieved": len(docs), "query": query[:50]})
        observability.log_agent_execution("RetrievalAgent", state, f"retrieved_{len(docs)}_docs")
        print(f"[RetrievalAgent] Retrieved {len(docs)} docs")
    except Exception as e:
        print(f"[RetrievalAgent] Error during retrieval: {e}")
        observability.log_tool_result(tool_call, None, str(e))
        state["retrieved_docs"] = []
        state["context"] = state.get("context", [])
    return state

