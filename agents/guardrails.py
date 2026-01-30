"""
Guardrails agent for safety and content filtering.
Handles: violence, self-harm, sexual content, hate speech, jailbreak attempts.
Includes leet speak detection and confidence thresholds.
"""
import re


# Leet speak character mappings
LEET_MAP = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
    '7': 't', '@': 'a', '!': 'i', '$': 's', '+': 't'
}

# Banned word patterns (normalized)
BANNED_PATTERNS = [
    r'\b(kill|destroy|attack|hurt|harm)\w*\b',
    r'\b(suicide|self.?harm|end.?life)\w*\b',
    r'\b(sex|sexual|porn|explicit)\w*\b',
    r'\b(hate|racist|discriminat)\w*\b',
    r'\b(jailbreak|forget.?instruction|ignore.?rule)\w*\b',
]


def normalize_leet(text):
    """Convert leet speak to normal text for detection."""
    normalized = text.lower()
    for leet_char, normal_char in LEET_MAP.items():
        normalized = normalized.replace(leet_char, normal_char)
    return normalized


def detect_banned_content(text):
    """Detect banned content including leet speak variations."""
    # Normalize leet speak
    normalized = normalize_leet(text)
    
    # Check against banned patterns
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True, pattern
    
    return False, None


def calculate_confidence(state):
    """Calculate confidence score for the response."""
    # Factors affecting confidence
    has_context = len(state.get("retrieved_docs", [])) > 0
    has_memory = len(state.get("past_incidents", [])) > 0
    has_reasoning = state.get("reasoning") is not None
    
    confidence = 0.5  # Base confidence
    
    if has_context:
        confidence += 0.2
    if has_memory:
        confidence += 0.15
    if has_reasoning:
        confidence += 0.15
    
    return min(confidence, 1.0)


def guard(state):
    """Apply safety and content filtering guardrails."""
    from backend.observability import observability
    
    ticket = state.get("ticket", "")
    response = state.get("response", "")
    
    tool_call = observability.log_tool_call("safety_check", "GuardrailsAgent", {"ticket": ticket[:100]})
    
    # Check ticket for banned content
    is_banned, pattern = detect_banned_content(ticket)
    
    if is_banned:
        state["action"] = "ESCALATE"
        state["escalation_reason"] = f"Banned content detected: {pattern}"
        state["confidence"] = 0.0
        
        observability.log_tool_result(tool_call, {"action": "ESCALATE", "reason": f"Banned: {pattern}"})
        observability.log_decision("GuardrailsAgent", "ESCALATE", f"Banned content pattern: {pattern}", {"pattern": pattern})
        observability.log_agent_execution("GuardrailsAgent", state, "guardrails_escalate")
        print(f"[Guardrails] Escalation triggered: {pattern}")
        return state
    
    # Check response for banned content
    if response:
        is_banned, pattern = detect_banned_content(response)
        if is_banned:
            state["action"] = "ESCALATE"
            state["escalation_reason"] = f"Response contains banned content: {pattern}"
            state["confidence"] = 0.0
            print(f"[Guardrails] Response blocked: {pattern}")
            return state
    
    # Calculate confidence
    confidence = calculate_confidence(state)
    print(f"[Guardrails] Calculated confidence: {confidence:.2f}")
    print(f"[Guardrails] State before setting confidence: has_reasoning={state.get('reasoning') is not None}, has_memory={len(state.get('past_incidents', [])) > 0}, has_context={len(state.get('retrieved_docs', [])) > 0}")
    state["confidence"] = confidence
    print(f"[Guardrails] Set confidence in state: {state.get('confidence')}")
    
    # Confidence threshold for auto-response
    CONFIDENCE_THRESHOLD = 0.6
    
    if confidence < CONFIDENCE_THRESHOLD:
        state["action"] = "ESCALATE"
        state["escalation_reason"] = f"Low confidence: {confidence:.2f} < {CONFIDENCE_THRESHOLD}"
        observability.log_agent_execution("GuardrailsAgent", state, "guardrails_escalate")
        print(f"[Guardrails] Low confidence ({confidence:.2f}), escalating")
        return state
    
    # Check for hallucination indicators
    if response and ("i don't know" in response.lower() or "uncertain" in response.lower()):
        state["action"] = "ESCALATE"
        state["escalation_reason"] = "Uncertain response detected"
        observability.log_agent_execution("GuardrailsAgent", state, "guardrails_escalate")
        print("[Guardrails] Uncertain response, escalating")
        return state
    
    state["action"] = "AUTO_RESPOND"
    
    observability.log_tool_result(tool_call, {"action": "AUTO_RESPOND", "confidence": confidence})
    observability.log_decision("GuardrailsAgent", "AUTO_RESPOND", f"Confidence: {confidence:.2f} >= 0.6", {"confidence": confidence})
    observability.log_agent_execution("GuardrailsAgent", state, "guardrails_auto_respond")
    print(f"[Guardrails] Safe (confidence: {confidence:.2f})")
    return state

