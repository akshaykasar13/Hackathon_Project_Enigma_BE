"""
Context summarization for long conversations.
Prevents unbounded context growth.
"""
from backend import config
from typing import List, Dict, Any
from datetime import datetime

def summarize_conversation(conversation_history: List[Dict[str, Any]], max_length: int = 10) -> str:
    """Summarize conversation history to prevent unbounded growth."""
    if len(conversation_history) <= max_length:
        return ""
    
    # Get oldest entries to summarize
    to_summarize = conversation_history[:-max_length]
    recent = conversation_history[-max_length:]
    
    if not to_summarize:
        return ""
    
    # Build summary
    summary_parts = [
        f"Previous conversation summary ({len(to_summarize)} interactions):"
    ]
    
    # Group by ticket type or priority
    high_priority = [c for c in to_summarize if c.get("priority") == "HIGH"]
    if high_priority:
        summary_parts.append(f"- {len(high_priority)} high-priority tickets processed")
    
    # Extract key themes
    tickets = [c.get("ticket", "") for c in to_summarize if c.get("ticket")]
    if tickets:
        # Simple keyword extraction
        all_text = " ".join(tickets).lower()
        keywords = {}
        for word in ["payment", "error", "timeout", "database", "api", "eu"]:
            if word in all_text:
                keywords[word] = all_text.count(word)
        
        if keywords:
            top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:3]
            summary_parts.append(f"- Common themes: {', '.join([k[0] for k in top_keywords])}")
    
    # Add outcomes summary
    outcomes = [c.get("action") for c in to_summarize if c.get("action")]
    if outcomes:
        auto_responded = outcomes.count("AUTO_RESPOND")
        escalated = outcomes.count("ESCALATE")
        summary_parts.append(f"- Outcomes: {auto_responded} auto-responded, {escalated} escalated")
    
    return " | ".join(summary_parts)

def summarize_context(context: List[str], max_items: int = 5) -> List[str]:
    """Summarize context list to prevent unbounded growth."""
    if len(context) <= max_items:
        return context
    
    # Keep most recent items
    return context[-max_items:]

def window_context(state: Dict[str, Any], max_context_length: int = 20):
    """Apply sliding window to context to prevent unbounded growth."""
    # Summarize working memory if too large
    working_memory = state.get("working_memory", [])
    if len(working_memory) > max_context_length:
        summary = summarize_conversation(working_memory, max_length=10)
        if summary:
            state["context_summary"] = summary
        state["working_memory"] = working_memory[-max_context_length:]
    
    # Trim context lists
    for key in ["context", "retrieved_docs", "past_incidents"]:
        if key in state and isinstance(state[key], list):
            if len(state[key]) > max_context_length:
                state[key] = summarize_context(state[key], max_items=max_context_length)
    
    return state

