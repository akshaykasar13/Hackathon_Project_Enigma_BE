"""
AI-specific observability: Token usage, costs, latency, and model performance tracking.
Tracks all LLM calls, embeddings, and AI-related operations.
"""
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

logger = logging.getLogger("agent_system")

# OpenAI pricing (as of 2024, update as needed)
# Prices per 1K tokens
PRICING = {
    "gpt-3.5-turbo": {
        "input": 0.0005,   # $0.50 per 1M tokens
        "output": 0.0015  # $1.50 per 1M tokens
    },
    "gpt-4": {
        "input": 0.03,    # $30 per 1M tokens
        "output": 0.06    # $60 per 1M tokens
    },
    "gpt-4-turbo": {
        "input": 0.01,    # $10 per 1M tokens
        "output": 0.03    # $30 per 1M tokens
    },
    "text-embedding-3-small": {
        "input": 0.02,    # $0.20 per 1M tokens
        "output": 0.0
    },
    "text-embedding-3-large": {
        "input": 0.13,    # $1.30 per 1M tokens
        "output": 0.0
    }
}

@dataclass
class LLMCall:
    """Represents a single LLM API call."""
    call_id: str
    model: str
    agent_name: str
    operation: str  # e.g., "response_generation", "intent_classification"
    task_id: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: str
    success: bool
    error: Optional[str] = None
    prompt_preview: Optional[str] = None  # First 200 chars
    response_preview: Optional[str] = None  # First 200 chars

@dataclass
class EmbeddingCall:
    """Represents an embedding API call."""
    call_id: str
    model: str
    operation: str  # e.g., "document_embedding", "memory_search"
    input_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: str
    success: bool
    error: Optional[str] = None

class AIMetricsTracker:
    """Tracks AI-related metrics: tokens, costs, latency, performance."""
    
    def __init__(self):
        self.llm_calls: List[LLMCall] = []
        self.embedding_calls: List[EmbeddingCall] = []
        self.max_calls = 10000  # Keep last 10K calls
        self._call_counter = 0
        
        # Aggregated metrics
        self._daily_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "llm_calls": 0,
            "embedding_calls": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_latency_ms": 0.0,
            "errors": 0,
            "by_model": defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0}),
            "by_agent": defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0}),
            "by_operation": defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
        })
    
    def _generate_call_id(self) -> str:
        """Generate unique call ID."""
        self._call_counter += 1
        return f"call_{int(time.time() * 1000)}_{self._call_counter}"
    
    def _get_date_key(self) -> str:
        """Get date key for daily aggregation."""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int = 0) -> float:
        """Calculate cost based on model and token usage."""
        if model not in PRICING:
            # Default to gpt-3.5-turbo pricing if unknown
            model = "gpt-3.5-turbo"
        
        pricing = PRICING[model]
        input_cost = (prompt_tokens / 1000) * pricing.get("input", 0)
        output_cost = (completion_tokens / 1000) * pricing.get("output", 0)
        return input_cost + output_cost
    
    def track_llm_call(
        self,
        model: str,
        agent_name: str,
        operation: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        task_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        prompt_preview: Optional[str] = None,
        response_preview: Optional[str] = None
    ) -> LLMCall:
        """Track an LLM API call."""
        call_id = self._generate_call_id()
        total_tokens = prompt_tokens + completion_tokens
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        
        call = LLMCall(
            call_id=call_id,
            model=model,
            agent_name=agent_name,
            operation=operation,
            task_id=task_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat(),
            success=success,
            error=error,
            prompt_preview=prompt_preview[:200] if prompt_preview else None,
            response_preview=response_preview[:200] if response_preview else None
        )
        
        self.llm_calls.append(call)
        self._trim_calls()
        
        # Update daily metrics
        date_key = self._get_date_key()
        metrics = self._daily_metrics[date_key]
        metrics["llm_calls"] += 1
        metrics["total_tokens"] += total_tokens
        metrics["total_cost_usd"] += cost
        metrics["total_latency_ms"] += latency_ms
        if not success:
            metrics["errors"] += 1
        
        metrics["by_model"][model]["calls"] += 1
        metrics["by_model"][model]["tokens"] += total_tokens
        metrics["by_model"][model]["cost"] += cost
        
        metrics["by_agent"][agent_name]["calls"] += 1
        metrics["by_agent"][agent_name]["tokens"] += total_tokens
        metrics["by_agent"][agent_name]["cost"] += cost
        
        metrics["by_operation"][operation]["calls"] += 1
        metrics["by_operation"][operation]["tokens"] += total_tokens
        metrics["by_operation"][operation]["cost"] += cost
        
        logger.info(
            f"[AI Metrics] LLM Call: {model} | {agent_name}/{operation} | "
            f"Tokens: {total_tokens} ({prompt_tokens}+{completion_tokens}) | "
            f"Cost: ${cost:.6f} | Latency: {latency_ms:.2f}ms"
        )
        
        return call
    
    def track_embedding_call(
        self,
        model: str,
        operation: str,
        input_tokens: int,
        latency_ms: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> EmbeddingCall:
        """Track an embedding API call."""
        call_id = self._generate_call_id()
        cost = self._calculate_cost(model, input_tokens, 0)
        
        call = EmbeddingCall(
            call_id=call_id,
            model=model,
            operation=operation,
            input_tokens=input_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat(),
            success=success,
            error=error
        )
        
        self.embedding_calls.append(call)
        self._trim_calls()
        
        # Update daily metrics
        date_key = self._get_date_key()
        metrics = self._daily_metrics[date_key]
        metrics["embedding_calls"] += 1
        metrics["total_tokens"] += input_tokens
        metrics["total_cost_usd"] += cost
        metrics["total_latency_ms"] += latency_ms
        if not success:
            metrics["errors"] += 1
        
        metrics["by_model"][model]["calls"] += 1
        metrics["by_model"][model]["tokens"] += input_tokens
        metrics["by_model"][model]["cost"] += cost
        
        metrics["by_operation"][operation]["calls"] += 1
        metrics["by_operation"][operation]["tokens"] += input_tokens
        metrics["by_operation"][operation]["cost"] += cost
        
        logger.info(
            f"[AI Metrics] Embedding: {model} | {operation} | "
            f"Tokens: {input_tokens} | Cost: ${cost:.6f} | Latency: {latency_ms:.2f}ms"
        )
        
        return call
    
    def _trim_calls(self):
        """Keep only recent calls."""
        if len(self.llm_calls) > self.max_calls:
            self.llm_calls = self.llm_calls[-self.max_calls:]
        if len(self.embedding_calls) > self.max_calls:
            self.embedding_calls = self.embedding_calls[-self.max_calls:]
    
    def get_summary(self, days: int = 1) -> Dict[str, Any]:
        """Get summary metrics for the last N days."""
        from datetime import datetime, timedelta
        
        summary = {
            "period_days": days,
            "total_llm_calls": 0,
            "total_embedding_calls": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "avg_latency_ms": 0.0,
            "error_rate": 0.0,
            "by_model": defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0}),
            "by_agent": defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0}),
            "by_operation": defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0}),
            "daily_breakdown": []
        }
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        for date_key, metrics in self._daily_metrics.items():
            if date_key >= cutoff_date:
                summary["total_llm_calls"] += metrics["llm_calls"]
                summary["total_embedding_calls"] += metrics["embedding_calls"]
                summary["total_tokens"] += metrics["total_tokens"]
                summary["total_cost_usd"] += metrics["total_cost_usd"]
                summary["total_latency_ms"] += metrics["total_latency_ms"]
                
                for model, data in metrics["by_model"].items():
                    summary["by_model"][model]["calls"] += data["calls"]
                    summary["by_model"][model]["tokens"] += data["tokens"]
                    summary["by_model"][model]["cost"] += data["cost"]
                
                for agent, data in metrics["by_agent"].items():
                    summary["by_agent"][agent]["calls"] += data["calls"]
                    summary["by_agent"][agent]["tokens"] += data["tokens"]
                    summary["by_agent"][agent]["cost"] += data["cost"]
                
                for op, data in metrics["by_operation"].items():
                    summary["by_operation"][op]["calls"] += data["calls"]
                    summary["by_operation"][op]["tokens"] += data["tokens"]
                    summary["by_operation"][op]["cost"] += data["cost"]
                
                total_calls = metrics["llm_calls"] + metrics["embedding_calls"]
                summary["daily_breakdown"].append({
                    "date": date_key,
                    "llm_calls": metrics["llm_calls"],
                    "embedding_calls": metrics["embedding_calls"],
                    "total_tokens": metrics["total_tokens"],
                    "cost_usd": metrics["total_cost_usd"],
                    "errors": metrics["errors"],
                    "error_rate": metrics["errors"] / total_calls if total_calls > 0 else 0.0
                })
        
        total_calls = summary["total_llm_calls"] + summary["total_embedding_calls"]
        if total_calls > 0:
            summary["avg_latency_ms"] = summary["total_latency_ms"] / total_calls
            summary["error_rate"] = sum(m["errors"] for m in summary["daily_breakdown"]) / total_calls
        
        # Convert defaultdicts to regular dicts for JSON serialization
        summary["by_model"] = dict(summary["by_model"])
        summary["by_agent"] = dict(summary["by_agent"])
        summary["by_operation"] = dict(summary["by_operation"])
        
        return summary
    
    def get_recent_llm_calls(self, limit: int = 100, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent LLM calls."""
        calls = self.llm_calls[-limit:]
        if task_id:
            calls = [c for c in calls if c.task_id == task_id]
        return [asdict(c) for c in calls]
    
    def get_recent_embedding_calls(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent embedding calls."""
        return [asdict(c) for c in self.embedding_calls[-limit:]]
    
    def export_metrics(self, filepath: str, days: int = 30):
        """Export metrics to JSON file."""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "summary": self.get_summary(days=days),
            "recent_llm_calls": self.get_recent_llm_calls(limit=1000),
            "recent_embedding_calls": self.get_recent_embedding_calls(limit=1000)
        }
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

# Global AI metrics tracker
ai_metrics = AIMetricsTracker()

