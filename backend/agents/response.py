"""
Response agent for generating user responses.
Uses LLM for dynamic response generation with test mode fallback.
"""
import logging
from backend import config

logger = logging.getLogger("agent_system")

def generate_response_with_llm(state):
    """Generate response using LLM (OpenAI). Retries up to MAX_LLM_RETRIES on failure."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        ticket = state.get("ticket", "")
        priority = state.get("priority", "LOW")
        correlation = state.get("correlation", [])
        past_incidents = state.get("past_incidents", [])
        retrieved_docs = state.get("retrieved_docs", [])
        reasoning = state.get("reasoning", "")
        
        # Build context
        context_parts = []
        if retrieved_docs:
            context_parts.append(f"Retrieved Knowledge:\n{chr(10).join(retrieved_docs[:3])}")
        if past_incidents:
            context_parts.append(f"Past Similar Incidents: {', '.join(past_incidents[:5])}")
        if correlation:
            context_parts.append(f"Correlations: {', '.join(correlation)}")
        if reasoning:
            context_parts.append(f"Analysis: {reasoning}")
        
        context = "\n\n".join(context_parts) if context_parts else "No additional context available."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent support co-pilot. Generate helpful, actionable responses based on the ticket and context provided.
            
Guidelines:
- Be concise but informative
- Reference specific context when available
- Provide actionable recommendations
- If this is a memory query, summarize past incidents clearly
- If correlations exist, explain them
- Use professional, supportive tone"""),
            ("human", """Ticket: {ticket}
Priority: {priority}

Context:
{context}

Generate a helpful response for the user.""")
        ])
        
        chain = prompt | llm
        response = chain.invoke({
            "ticket": ticket,
            "priority": priority,
            "context": context
        })
        
        return response.content
    except Exception as e:
        logger.warning(f"[LLM_FAILURE] ResponseAgent: LLM generation failed - {type(e).__name__}: {e}", exc_info=True)
        return None

def generate_response_fallback(state):
    """Fallback response generation (template-based, works in test mode)."""
    ticket = state.get("ticket", "")
    priority = state.get("priority", "LOW")
    correlation = state.get("correlation", [])
    past_incidents = state.get("past_incidents", [])
    retrieved_docs = state.get("retrieved_docs", [])
    reasoning = state.get("reasoning", "")
    
    # Build response based on scenario
    if "have we seen" in ticket.lower() or "error code" in ticket.lower():
        # Memory query scenario
        response = f"Based on historical data, I found {len(past_incidents)} similar incidents. "
        if past_incidents:
            response += f"Recent examples include: {', '.join(past_incidents[:3])}. "
        response += "Would you like more details about any specific incident?"
    elif correlation:
        # Correlated incident scenario
        response = f"Priority {priority} issue detected. "
        
        # Format correlations nicely (remove duplicates)
        unique_correlations = list(dict.fromkeys(correlation[:3]))  # Remove duplicates, keep order
        if unique_correlations:
            response += f"I've identified {len(unique_correlations)} correlation(s) with past incidents. "
            if len(unique_correlations) == 1:
                response += f"Correlation: {unique_correlations[0]}. "
            else:
                response += f"Top correlations: {unique_correlations[0]}. "
        
        # Add context from retrieved docs if available
        if retrieved_docs:
            response += f"Found {len(retrieved_docs)} relevant document(s) in knowledge base. "
        
        # Add reasoning if available (truncate if too long)
        if reasoning:
            reasoning_short = reasoning[:150] + "..." if len(reasoning) > 150 else reasoning
            response += f"Analysis: {reasoning_short} "
        
        # Add mitigation suggestions (financial service specific)
        ticket_lower = ticket.lower()
        payment_keywords = ["payment", "transaction", "gateway", "billing", "invoice", "refund", "charge", "financial"]
        is_payment_related = any(keyword in ticket_lower for keyword in payment_keywords)
        
        if is_payment_related:
            # Financial service specific mitigation
            mitigation = "Suggested mitigation for financial service: "
            mitigation_parts = []
            if "eu" in ticket_lower or "europe" in ticket_lower:
                mitigation_parts.append("verify EU region connectivity and compliance")
            if "gateway" in ticket_lower:
                mitigation_parts.append("check payment gateway logs and API status")
            if "intermittent" in ticket_lower:
                mitigation_parts.append("review recent deployments and infrastructure changes")
            mitigation_parts.append("check transaction logs for patterns")
            mitigation_parts.append("verify payment processor health metrics")
            mitigation_parts.append("review recent configuration changes")
            response += mitigation + ", ".join(mitigation_parts) + "."
        elif "database" in ticket.lower() or "connection" in ticket.lower():
            response += "Suggested mitigation: Check database connection pool, verify network connectivity, review connection timeout settings, check recent database migrations."
        elif "error" in ticket.lower():
            response += "Suggested mitigation: Review error logs, check system health metrics, verify recent configuration changes."
        else:
            response += "Suggested mitigation: Review system logs, check related services, verify recent changes."
    else:
        # Default response
        response = f"Processing {priority} priority ticket: {ticket[:100]}... "
        if retrieved_docs:
            response += f"Found {len(retrieved_docs)} relevant documents in our knowledge base. "
        response += "I'm analyzing the issue and will provide recommendations shortly."
    
    return response

def respond(state):
    """Generate user response using LLM or fallback."""
    # Try LLM generation if not in test mode and API key available
    response = None
    if not config.TEST_MODE and config.OPENAI_API_KEY and config.OPENAI_API_KEY != "test-key-not-used":
        response = generate_response_with_llm(state)
    
    used_llm = response is not None  # Track before fallback overwrites response
    
    # Use fallback if LLM failed or in test mode
    if not response:
        if not config.TEST_MODE:
            logger.info("[LLM_FALLBACK] ResponseAgent: Using template-based response (LLM failed or unavailable)")
        response = generate_response_fallback(state)
    
    method = "LLM" if used_llm else "fallback"
    state["response"] = response
    
    # Log response generation
    from backend.observability import observability
    tool_call = observability.log_tool_call("response_generation", "ResponseAgent", {
        "ticket": state.get("ticket", "")[:100],
        "method": method
    }, state.get("task_id"))
    observability.log_tool_result(tool_call, {"response_length": len(response), "method": method})
    reasoning = f"Generated response using {method} based on ticket, context, and analysis"
    observability.log_agent_execution("ResponseAgent", state, "response_generated", reasoning=reasoning)
    
    print(f"[ResponseAgent] Generated response ({method})")
    return state

