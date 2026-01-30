"""
Structured logging and observability for agent system.
Tracks tool calls, execution steps, and results.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

# Create logs directory (resolve relative to this file)
try:
    from backend import config
    LOG_DIR = Path(config.BACKEND_ROOT) / "logs"
except ImportError:
    LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "agent_system.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("agent_system")

class ToolCall:
    """Represents a tool call with inputs, execution, and results."""
    def __init__(self, tool_name: str, agent_name: str, inputs: Dict[str, Any], task_id: Optional[str] = None):
        self.tool_name = tool_name
        self.agent_name = agent_name
        self.inputs = inputs
        self.task_id = task_id
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.execution_time_ms: Optional[float] = None
    
    def complete(self, result: Any = None, error: Optional[str] = None):
        """Mark tool call as complete."""
        self.end_time = datetime.now()
        self.result = result
        self.error = error
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.execution_time_ms = delta.total_seconds() * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tool_name": self.tool_name,
            "agent_name": self.agent_name,
            "task_id": self.task_id,
            "inputs": self.inputs,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "status": "error" if self.error else "success" if self.end_time else "running"
        }

class ObservabilityLogger:
    """Centralized observability logger for agent system."""
    
    def __init__(self):
        self.tool_calls: List[ToolCall] = []
        self.agent_events: List[Dict[str, Any]] = []
        self.max_events = 1000  # Keep last 1000 events
    
    def log_tool_call(self, tool_name: str, agent_name: str, inputs: Dict[str, Any], task_id: Optional[str] = None) -> ToolCall:
        """Log a tool call start."""
        tool_call = ToolCall(tool_name, agent_name, inputs, task_id)
        self.tool_calls.append(tool_call)
        
        event = {
            "type": "tool_call_start",
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "agent_name": agent_name,
            "task_id": task_id,
            "inputs": inputs
        }
        self.agent_events.append(event)
        self._trim_events()
        
        logger.info(f"[{agent_name}] Tool call: {tool_name}", extra={"inputs": inputs})
        return tool_call
    
    def log_tool_result(self, tool_call: ToolCall, result: Any = None, error: Optional[str] = None):
        """Log a tool call completion."""
        tool_call.complete(result, error)
        
        event = {
            "type": "tool_call_end",
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_call.tool_name,
            "agent_name": tool_call.agent_name,
            "task_id": tool_call.task_id,
            "result": str(result) if result is not None else None,
            "error": error,
            "execution_time_ms": tool_call.execution_time_ms
        }
        self.agent_events.append(event)
        self._trim_events()
        
        if error:
            logger.error(f"[{tool_call.agent_name}] Tool {tool_call.tool_name} failed: {error}")
        else:
            logger.info(f"[{tool_call.agent_name}] Tool {tool_call.tool_name} completed in {tool_call.execution_time_ms:.2f}ms")
    
    def log_agent_execution(self, agent_name: str, state: Dict[str, Any], action: str = "executed", reasoning: Optional[str] = None):
        """Log agent execution. Optional reasoning for display in execution trace."""
        event = {
            "type": "agent_execution",
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "task_id": state.get("task_id") if isinstance(state, dict) else None,
            "action": action,
            "reasoning": reasoning,
            "state_snapshot": {
                "priority": state.get("priority"),
                "ticket": state.get("ticket", "")[:100],  # Truncate for logging
                "has_context": len(state.get("context", [])) > 0,
                "has_memory": len(state.get("past_incidents", [])) > 0
            }
        }
        self.agent_events.append(event)
        self._trim_events()
        
        logger.info(f"[{agent_name}] {action}")
    
    def log_decision(self, agent_name: str, decision: str, reasoning: str, data_used: Dict[str, Any], task_id: Optional[str] = None):
        """Log a decision made by an agent."""
        event = {
            "type": "decision",
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "task_id": task_id,
            "decision": decision,
            "reasoning": reasoning,
            "data_used": data_used
        }
        self.agent_events.append(event)
        self._trim_events()
        
        logger.info(f"[{agent_name}] Decision: {decision} | Reasoning: {reasoning}")
    
    def get_recent_events(self, limit: int = 100, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent events, optionally filtered by task_id."""
        events = self.agent_events[-limit:]
        if task_id:
            events = [e for e in events if e.get("task_id") == task_id]
        return events
    
    def get_events_by_task_id(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all events for a specific task_id, in execution order."""
        return [e for e in self.agent_events if e.get("task_id") == task_id]
    
    def get_tool_calls(self, agent_name: Optional[str] = None, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tool calls, optionally filtered by agent or task_id."""
        calls = self.tool_calls
        if agent_name:
            calls = [c for c in calls if c.agent_name == agent_name]
        if task_id:
            calls = [c for c in calls if c.task_id == task_id]
        return [c.to_dict() for c in calls]
    
    def _trim_events(self):
        """Keep only recent events."""
        if len(self.agent_events) > self.max_events:
            self.agent_events = self.agent_events[-self.max_events:]
        if len(self.tool_calls) > self.max_events:
            self.tool_calls = self.tool_calls[-self.max_events:]
    
    def export_logs(self, filepath: str):
        """Export logs to JSON file."""
        export_data = {
            "tool_calls": self.get_tool_calls(),
            "recent_events": self.get_recent_events(500),
            "exported_at": datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

# Global observability logger instance
observability = ObservabilityLogger()

