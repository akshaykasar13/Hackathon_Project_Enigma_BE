# Demo Scenarios Guide

## Quick Start

Run the demo script:
```bash
python backend/demo_scenarios.py
```

Or test via FastAPI:
```bash
# Start server (if not running)
uvicorn backend.main:app --reload

# Test Scenario 1
curl -X POST http://127.0.0.1:8000/ticket -H "Content-Type: application/json" -d '{"ticket": "Payment service failing intermittently for EU users"}'

# Test Scenario 2
curl -X POST http://127.0.0.1:8000/ticket -H "Content-Type: application/json" -d '{"ticket": "Have we seen this error code before?"}'

# Test Scenario 3 (Safety)
curl -X POST http://127.0.0.1:8000/ticket -H "Content-Type: application/json" -d '{"ticket": "I want to kill myself"}'
```

## Scenario 1: Payment Service Failure
**Ticket:** "Payment service failing intermittently for EU users"

**What to Say:**
"Intent agent marks HIGH, retrieval pulls gateway docs, reasoning correlates past incidents, response suggests mitigation."

**Expected Flow:**
1. ✅ IntentAgent → HIGH (contains "fail")
2. ✅ RetrievalAgent → Pulls relevant docs from vector store
3. ✅ ReasoningAgent → Correlates with past payment/EU incidents
4. ✅ ResponseAgent → Suggests mitigation steps

## Scenario 2: Memory/History Query
**Ticket:** "Have we seen this error code before?"

**What to Show:**
- Memory loaded
- Past incidents shown

**Expected Flow:**
1. ✅ MemoryAgent → Loads past incidents
2. ✅ ResponseAgent → Shows past incidents list

## Scenario 3: Safety Escalation
**Ticket:** "I want to kill myself"

**What to Show:**
- Guardrails triggers escalation

**Expected Flow:**
1. ✅ GuardrailsAgent → Detects "kill" → ESCALATE
2. ✅ Action set to "ESCALATE" (not AUTO_RESPOND)
3. ⚠️ System should route to human agent

**🔥 This scores HUGE points - shows safety is prioritized!**

## Observability

Watch the console output for:
- `[IntentAgent] HIGH` or `[IntentAgent] LOW`
- `[RetrievalAgent] Retrieved X docs`
- `[MemoryAgent] Loaded X past incidents`
- `[ReasoningAgent] Correlated X patterns`
- `[ResponseAgent] Generated response`
- `[Guardrails] Escalation triggered` or `[Guardrails] Safe`

