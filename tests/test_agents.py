"""
Comprehensive tests for all agents.
"""
import os
import sys
import pytest

# Set test mode
os.environ["TEST_MODE"] = "true"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.ingestion import ingest
from backend.agents.planner import plan
from backend.agents.intent import classify
from backend.agents.retrieval import retrieve
from backend.agents.memory import load_memory, save_memory
from backend.agents.reasoning import reason
from backend.agents.response import respond
from backend.agents.guardrails import guard

class TestIngestionAgent:
    def test_ingest_basic(self):
        state = {"input": "Test ticket"}
        result = ingest(state)
        assert "ticket" in result
        assert result["ticket"] == "Test ticket"
    
    def test_ingest_empty(self):
        state = {"input": ""}
        result = ingest(state)
        assert "ticket" in result

class TestPlannerAgent:
    def test_plan_high_priority(self):
        state = {"ticket": "Payment service failing"}
        result = plan(state)
        assert "execution_strategy" in result
        assert result["execution_strategy"]["mode"] == "parallel"
    
    def test_plan_low_priority(self):
        state = {"ticket": "How do I reset password?"}
        result = plan(state)
        assert "execution_strategy" in result

class TestIntentAgent:
    def test_classify_high_priority(self):
        state = {"ticket": "Payment service failing"}
        result = classify(state)
        assert result["priority"] == "HIGH"
    
    def test_classify_low_priority(self):
        state = {"ticket": "How do I reset password?"}
        result = classify(state)
        assert result["priority"] == "LOW"

class TestGuardrailsAgent:
    def test_guard_safe_input(self):
        state = {"ticket": "How do I reset password?", "response": "Here's how to reset..."}
        result = guard(state)
        assert "action" in result
        assert result["action"] in ["AUTO_RESPOND", "ESCALATE"]
    
    def test_guard_banned_content(self):
        state = {"ticket": "I want to kill myself"}
        result = guard(state)
        assert result["action"] == "ESCALATE"
        assert "escalation_reason" in result
    
    def test_guard_leet_speak(self):
        state = {"ticket": "D3str0y 3v3ryth1ng"}
        result = guard(state)
        assert result["action"] == "ESCALATE"

class TestResponseAgent:
    def test_respond_basic(self):
        state = {
            "ticket": "Test ticket",
            "priority": "LOW",
            "correlation": [],
            "past_incidents": []
        }
        result = respond(state)
        assert "response" in result
        assert len(result["response"]) > 0

class TestReasoningAgent:
    def test_reason_basic(self):
        state = {
            "ticket": "Payment service failing",
            "priority": "HIGH",
            "context": [],
            "past_incidents": ["Payment service failing"]
        }
        result = reason(state)
        assert "reasoning" in result
        assert "correlation" in result

class TestMemoryAgent:
    def test_load_memory(self):
        state = {
            "ticket": "Test ticket",
            "task_id": "test-123",
            "timestamp": "2024-01-01T00:00:00"
        }
        result = load_memory(state)
        assert "working_memory" in result
        assert "episodic_memory" in result
    
    def test_save_memory(self):
        state = {
            "ticket": "Test ticket",
            "response": "Test response",
            "action": "AUTO_RESPOND",
            "priority": "LOW"
        }
        result = save_memory(state)
        assert result == state  # Should return state unchanged

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

