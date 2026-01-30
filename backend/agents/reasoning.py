"""
Reasoning agent for logical reasoning and problem-solving.
Uses OpenAI LLM for root cause analysis and semantic similarity for correlation.
"""
import logging
from backend import config
from backend.memory.storage import memory_storage

logger = logging.getLogger("agent_system")

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

def analyze_with_llm(ticket: str, correlations: list, patterns: list, retrieved_docs: list, past_incidents: list) -> dict:
    """Use OpenAI LLM for deep root cause analysis and recommendations."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Build context for LLM
        context_parts = []
        if correlations:
            corr_text = "\n".join([f"- {c['incident']} (similarity: {c['similarity']})" for c in correlations[:3]])
            context_parts.append(f"Similar past incidents:\n{corr_text}")
        if patterns:
            context_parts.append(f"Detected patterns: {', '.join(patterns)}")
        if retrieved_docs:
            docs_text = "\n".join([f"- {doc[:100]}..." for doc in retrieved_docs[:2]])
            context_parts.append(f"Relevant documentation:\n{docs_text}")
        
        context = "\n\n".join(context_parts) if context_parts else "No additional context available."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a support system analyst. Analyze the ticket and provide root cause analysis.

Respond with ONLY a JSON object (no markdown):

{{
    "root_cause": "most likely root cause (1-2 sentences)",
    "confidence": "high" or "medium" or "low",
    "category": "technical" or "billing" or "data_issue" or "user_error" or "system_bug" or "configuration",
    "impact": "high" or "medium" or "low",
    "recommended_actions": ["action 1", "action 2", "action 3"],
    "escalation_needed": true/false,
    "reasoning_summary": "brief explanation of your analysis (2-3 sentences)"
}}

Be specific and actionable. Consider the context provided."""),
            ("human", """Ticket: {ticket}

Context:
{context}

Provide your analysis.""")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"ticket": ticket, "context": context})
        
        import json
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content)
        
        return {
            "root_cause": result.get("root_cause", "Unable to determine"),
            "confidence": result.get("confidence", "medium"),
            "category": result.get("category", "general"),
            "impact": result.get("impact", "medium"),
            "recommended_actions": result.get("recommended_actions", []),
            "escalation_needed": result.get("escalation_needed", False),
            "reasoning_summary": result.get("reasoning_summary", "LLM analysis"),
            "method": "LLM"
        }
    except Exception as e:
        logger.warning(f"[LLM_FAILURE] ReasoningAgent: LLM analysis failed - {type(e).__name__}: {e}", exc_info=True)
        return None


def analyze_with_rules(ticket: str, correlations: list, patterns: list) -> dict:
    """Fallback rule-based analysis."""
    ticket_lower = ticket.lower()
    
    # Determine category
    category = "general"
    if any(kw in ticket_lower for kw in ["payment", "billing", "invoice", "charge"]):
        category = "billing"
    elif any(kw in ticket_lower for kw in ["error", "bug", "crash", "fail"]):
        category = "technical"
    elif any(kw in ticket_lower for kw in ["mismatch", "wrong", "incorrect", "received", "sent"]):
        category = "data_issue"
    
    # Determine impact
    impact = "medium"
    if any(kw in ticket_lower for kw in ["urgent", "critical", "down", "all users"]):
        impact = "high"
    elif any(kw in ticket_lower for kw in ["minor", "small", "sometimes"]):
        impact = "low"
    
    # Generate basic recommendations
    actions = []
    if category == "billing":
        actions = ["Review transaction logs", "Check billing records", "Verify account status"]
    elif category == "technical":
        actions = ["Check error logs", "Review recent deployments", "Verify system health"]
    elif category == "data_issue":
        actions = ["Verify data integrity", "Check data sync processes", "Review input validation"]
    else:
        actions = ["Gather more information", "Check related systems", "Review recent changes"]
    
    return {
        "root_cause": f"Potential {category} issue based on ticket content",
        "confidence": "medium" if correlations else "low",
        "category": category,
        "impact": impact,
        "recommended_actions": actions,
        "escalation_needed": impact == "high",
        "reasoning_summary": f"Rule-based analysis: {category} issue with {impact} impact",
        "method": "rules"
    }


def reason(state):
    """Perform logical reasoning and problem-solving with LLM-powered analysis."""
    priority = state.get("priority", "LOW")
    context = state.get("context", [])
    retrieved_docs = state.get("retrieved_docs", [])
    past_incidents = state.get("past_incidents", [])
    ticket = state.get("ticket", "")
    
    # Find correlated incidents using semantic similarity
    correlations = find_correlated_incidents(ticket, past_incidents)
    
    # Identify patterns (rule-based)
    patterns = identify_patterns(ticket, past_incidents, correlations)
    
    # Use LLM for deep analysis (if available)
    llm_analysis = None
    if not config.TEST_MODE and config.OPENAI_API_KEY and config.OPENAI_API_KEY != "test-key-not-used":
        llm_analysis = analyze_with_llm(ticket, correlations, patterns, retrieved_docs, past_incidents)
    
    # Fallback to rules if LLM failed
    if not llm_analysis:
        if not config.TEST_MODE:
            logger.info("[LLM_FALLBACK] ReasoningAgent: Using rule-based analysis (LLM failed or unavailable)")
        llm_analysis = analyze_with_rules(ticket, correlations, patterns)
    
    # Build reasoning summary
    reasoning_parts = [
        f"Priority: {priority}",
        f"Category: {llm_analysis['category']}",
        f"Impact: {llm_analysis['impact']}",
        f"Root cause: {llm_analysis['root_cause']}",
        f"Confidence: {llm_analysis['confidence']}",
        f"Analysis method: {llm_analysis['method']}"
    ]
    
    if correlations:
        reasoning_parts.append(f"Related incidents: {len(correlations)}")
    
    if patterns:
        reasoning_parts.append(f"Patterns: {'; '.join(patterns)}")
    
    # Build correlation summary for state (remove duplicates)
    correlation_summary = []
    seen_correlations = set()
    for corr in correlations[:3]:  # Top 3
        corr_str = f"{corr['reason']} (similarity: {corr['similarity']:.2f})"
        if corr_str not in seen_correlations:
            correlation_summary.append(corr_str)
            seen_correlations.add(corr_str)
    
    state["reasoning"] = " | ".join(reasoning_parts)
    state["correlation"] = correlation_summary if correlation_summary else []
    state["correlation_details"] = correlations
    state["patterns"] = patterns
    state["root_cause_analysis"] = {
        "root_cause": llm_analysis["root_cause"],
        "confidence": llm_analysis["confidence"],
        "category": llm_analysis["category"],
        "impact": llm_analysis["impact"],
        "recommended_actions": llm_analysis["recommended_actions"],
        "escalation_needed": llm_analysis["escalation_needed"],
        "method": llm_analysis["method"]
    }
    
    # Log reasoning decision
    from backend.observability import observability
    observability.log_decision("ReasoningAgent", f"analysis_{llm_analysis['category']}", 
                              f"{llm_analysis['reasoning_summary']} (via {llm_analysis['method']})",
                              {
                                  "correlations_count": len(correlations), 
                                  "patterns": patterns,
                                  "root_cause": llm_analysis["root_cause"],
                                  "confidence": llm_analysis["confidence"]
                              }, state.get("task_id"))
    observability.log_agent_execution("ReasoningAgent", state, "analysis_complete")
    
    print(f"[ReasoningAgent] {llm_analysis['category']} issue, {llm_analysis['impact']} impact, {len(correlations)} correlations (via {llm_analysis['method']})")
    return state

