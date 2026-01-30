"""
Intent agent for understanding user intent.
Uses OpenAI LLM for intelligent classification with rule-based fallback.
"""
import logging
from backend import config
from backend.observability import observability

logger = logging.getLogger("agent_system")


def classify_with_llm(text: str) -> dict:
    """Use OpenAI LLM to classify ticket intent, urgency, and priority."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a support ticket classifier. Analyze the ticket and respond with ONLY a JSON object (no markdown, no explanation).

Classify:
1. priority: "HIGH" or "LOW"
   - HIGH: errors, failures, outages, data mismatches, financial issues, urgent requests, HTTP error codes (4xx, 5xx), system down, broken functionality
   - LOW: questions, feature requests, general inquiries, non-urgent issues

2. intent: brief description of what the user wants (max 10 words)

3. reasoning: why you chose this priority (max 20 words)

4. categories: list of relevant categories (e.g., ["billing", "technical", "error"])

Respond ONLY with JSON like:
{{"priority": "HIGH", "intent": "report quantity mismatch", "reasoning": "data discrepancy between received and sent amounts", "categories": ["billing", "data_issue"]}}"""),
            ("human", "{ticket}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"ticket": text})
        
        # Parse JSON response
        import json
        content = response.content.strip()
        # Handle potential markdown code blocks
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content)
        
        return {
            "priority": result.get("priority", "LOW").upper(),
            "intent": result.get("intent", "unknown"),
            "reasoning": result.get("reasoning", "LLM classification"),
            "categories": result.get("categories", []),
            "method": "LLM"
        }
    except Exception as e:
        logger.warning(f"[LLM_FAILURE] IntentAgent: LLM classification failed - {type(e).__name__}: {e}", exc_info=True)
        return None


def classify_with_rules(text: str) -> dict:
    """Fallback rule-based classification."""
    text_lower = text.lower()
    
    # Financial service priority detection
    payment_keywords = ["payment", "transaction", "gateway", "billing", "invoice", "refund", "charge", "financial"]
    is_payment_related = any(keyword in text_lower for keyword in payment_keywords)
    
    # High priority indicators
    high_priority_indicators = ["fail", "error", "down", "broken", "urgent", "critical", "outage", "500", "404", "400", "403", "mismatch", "wrong", "incorrect"]
    is_high_priority = any(indicator in text_lower for indicator in high_priority_indicators)
    
    # Check for numeric discrepancies (e.g., "received 400 but sent 100")
    import re
    numbers = re.findall(r'\d+', text)
    has_number_mismatch = len(numbers) >= 2 and len(set(numbers)) > 1
    
    # Determine priority
    if is_payment_related and (is_high_priority or "intermittent" in text_lower or "slow" in text_lower):
        priority = "HIGH"
        reasoning = "Payment-related issue with error indicators"
    elif is_high_priority:
        priority = "HIGH"
        reasoning = "Contains error/failure indicators"
    elif has_number_mismatch and any(word in text_lower for word in ["received", "sent", "expected", "got", "but"]):
        priority = "HIGH"
        reasoning = "Numeric mismatch detected (potential data discrepancy)"
    else:
        priority = "LOW"
        reasoning = "No urgent indicators detected"
    
    categories = []
    if is_payment_related:
        categories.append("billing")
    if is_high_priority:
        categories.append("technical")
    if has_number_mismatch:
        categories.append("data_issue")
    
    return {
        "priority": priority,
        "intent": "support request",
        "reasoning": reasoning,
        "categories": categories,
        "method": "rules"
    }


def classify(state):
    """Classify user intent using LLM (with rule-based fallback)."""
    tool_call = observability.log_tool_call("intent_classification", "IntentAgent", {"ticket": state.get("ticket", "")[:100]}, state.get("task_id"))
    
    try:
        text = state.get("ticket", "")
        
        # Try LLM classification first (if not in test mode)
        result = None
        if not config.TEST_MODE and config.OPENAI_API_KEY and config.OPENAI_API_KEY != "test-key-not-used":
            result = classify_with_llm(text)
        
        # Fallback to rules if LLM failed or in test mode
        if not result:
            if not config.TEST_MODE:
                logger.info("[LLM_FALLBACK] IntentAgent: Using rule-based classification (LLM failed or unavailable)")
            result = classify_with_rules(text)
        
        priority = result["priority"]
        reasoning = result["reasoning"]
        method = result["method"]
        
        state["priority"] = priority
        state["intent_details"] = {
            "intent": result.get("intent"),
            "categories": result.get("categories", []),
            "reasoning": reasoning,
            "method": method
        }
        
        observability.log_tool_result(tool_call, {"priority": priority, "method": method})
        observability.log_decision("IntentAgent", f"Classified as {priority}", 
                                  f"{reasoning} (via {method})", 
                                  {"ticket_text": text[:50], "categories": result.get("categories", [])}, 
                                  state.get("task_id"))
        observability.log_agent_execution("IntentAgent", state, f"classified_{priority.lower()}")
        print(f"[IntentAgent] {priority} (via {method}): {reasoning}")
    except Exception as e:
        observability.log_tool_result(tool_call, None, str(e))
        raise
    
    return state

