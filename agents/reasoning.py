"""
Reasoning agent for logical reasoning and problem-solving.
Uses semantic similarity for better correlation analysis.
"""
from backend import config
from backend.memory.storage import memory_storage

def calculate_semantic_similarity(text1, text2):
    """Calculate semantic similarity using embeddings (if available)."""
    if config.TEST_MODE or not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "test-key-not-used":
        # Fallback: simple keyword overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    try:
        from langchain_openai import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
        emb1 = embeddings.embed_query(text1)
        emb2 = embeddings.embed_query(text2)
        
        # Calculate cosine similarity manually (no sklearn/numpy dependency required)
        # Cosine similarity: dot product / (norm1 * norm2)
        if len(emb1) != len(emb2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a * a for a in emb1) ** 0.5
        norm2 = sum(b * b for b in emb2) ** 0.5
        similarity = dot_product / (norm1 * norm2) if (norm1 * norm2) > 0 else 0.0
        
        return float(similarity)
    except Exception as e:
        print(f"[ReasoningAgent] Embedding similarity failed: {e}, using keyword fallback")
        # Fallback to keyword matching
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0

def find_correlated_incidents(ticket, past_incidents, threshold=0.3):
    """Find incidents correlated with current ticket using semantic similarity."""
    correlations = []
    ticket_lower = ticket.lower()
    
    # Extract key patterns from ticket
    key_terms = []
    if "payment" in ticket_lower:
        key_terms.append("payment")
    if "error" in ticket_lower or "fail" in ticket_lower:
        key_terms.append("error")
    if "eu" in ticket_lower or "europe" in ticket_lower:
        key_terms.append("eu")
    if "timeout" in ticket_lower:
        key_terms.append("timeout")
    if "database" in ticket_lower or "db" in ticket_lower:
        key_terms.append("database")
    if "api" in ticket_lower:
        key_terms.append("api")
    
    # Find semantically similar incidents
    seen_incidents = set()  # Track incidents to avoid duplicates
    for incident in past_incidents[:20]:  # Check top 20 most recent
        if not incident:
            continue
        
        # Skip if we've already processed this exact incident
        incident_normalized = incident.lower().strip()
        if incident_normalized in seen_incidents:
            continue
        seen_incidents.add(incident_normalized)
        
        incident_lower = incident.lower()
        
        # Calculate semantic similarity
        similarity = calculate_semantic_similarity(ticket, incident)
        
        # Also check keyword matches
        keyword_match = any(term in incident_lower for term in key_terms)
        
        # If similarity is high or keywords match, add correlation
        if similarity >= threshold or keyword_match:
            correlation_type = "high" if similarity >= 0.6 else "medium" if similarity >= 0.4 else "low"
            
            # Determine specific correlation reason
            reason = []
            if similarity >= 0.5:
                reason.append("Semantically similar")
            if keyword_match:
                matched_terms = [t for t in key_terms if t in incident_lower]
                if matched_terms:
                    reason.append(f"Shared terms: {', '.join(matched_terms)}")
            
            if reason:
                correlations.append({
                    "incident": incident[:100] + "..." if len(incident) > 100 else incident,
                    "similarity": round(similarity, 2),
                    "type": correlation_type,
                    "reason": " | ".join(reason)
                })
    
    # Sort by similarity
    correlations.sort(key=lambda x: x["similarity"], reverse=True)
    return correlations[:5]  # Top 5 correlations

def identify_patterns(ticket, past_incidents, correlations):
    """Identify patterns and root causes."""
    patterns = []
    ticket_lower = ticket.lower()
    
    # Pattern: Recurring issues
    if len(correlations) >= 3:
        patterns.append("Recurring issue pattern detected - multiple similar incidents found")
    
    # Pattern: Region-specific
    if "eu" in ticket_lower or "europe" in ticket_lower:
        eu_incidents = [c for c in correlations if "eu" in c["incident"].lower()]
        if len(eu_incidents) >= 2:
            patterns.append("EU region appears to be a common factor")
    
    # Pattern: Financial service-specific
    payment_keywords = ["payment", "transaction", "gateway", "billing", "invoice", "refund", "charge", "financial"]
    is_payment_related = any(keyword in ticket_lower for keyword in payment_keywords)
    
    if is_payment_related:
        payment_incidents = [c for c in correlations if any(kw in c["incident"].lower() for kw in payment_keywords)]
        if len(payment_incidents) >= 2:
            patterns.append("Financial service shows recurring issues - requires immediate attention")
        elif len(payment_incidents) >= 1:
            patterns.append("Financial service incident detected - high business impact")
    
    # Pattern: Error type
    if "timeout" in ticket_lower:
        patterns.append("Timeout-related issues may indicate infrastructure problems")
    elif "connection" in ticket_lower:
        patterns.append("Connection issues may indicate network or service dependencies")
    
    return patterns

def reason(state):
    """Perform logical reasoning and problem-solving with semantic correlation."""
    priority = state.get("priority", "LOW")
    context = state.get("context", [])
    retrieved_docs = state.get("retrieved_docs", [])
    past_incidents = state.get("past_incidents", [])
    ticket = state.get("ticket", "")
    
    # Find correlated incidents using semantic similarity
    correlations = find_correlated_incidents(ticket, past_incidents)
    
    # Identify patterns
    patterns = identify_patterns(ticket, past_incidents, correlations)
    
    # Build reasoning summary
    reasoning_parts = [
        f"Priority: {priority}",
        f"Retrieved documents: {len(retrieved_docs)}",
        f"Historical incidents analyzed: {len(past_incidents)}",
        f"Correlations found: {len(correlations)}"
    ]
    
    if correlations:
        top_correlation = correlations[0]
        reasoning_parts.append(f"Strongest correlation: {top_correlation['similarity']:.2f} similarity ({top_correlation['type']})")
    
    if patterns:
        reasoning_parts.append(f"Patterns: {'; '.join(patterns)}")
    
    # Build correlation summary for state (remove duplicates)
    correlation_summary = []
    seen_correlations = set()
    for corr in correlations[:3]:  # Top 3
        corr_str = f"{corr['reason']} (similarity: {corr['similarity']:.2f})"
        # Only add if not already seen (deduplicate)
        if corr_str not in seen_correlations:
            correlation_summary.append(corr_str)
            seen_correlations.add(corr_str)
    
    state["reasoning"] = " | ".join(reasoning_parts)
    state["correlation"] = correlation_summary if correlation_summary else []
    state["correlation_details"] = correlations  # Store detailed correlations
    state["patterns"] = patterns
    
    # Log reasoning decision
    from backend.observability import observability
    observability.log_decision("ReasoningAgent", "correlation_analysis", 
                              f"Found {len(correlations)} correlations, {len(patterns)} patterns",
                              {"correlations_count": len(correlations), "patterns": patterns})
    observability.log_agent_execution("ReasoningAgent", state, "correlation_complete")
    
    print(f"[ReasoningAgent] Found {len(correlations)} correlations, {len(patterns)} patterns")
    return state

