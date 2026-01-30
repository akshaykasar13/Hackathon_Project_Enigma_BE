"""
Main entry point for the backend application.
"""
# Import config first to initialize environment variables and LangSmith
from backend import config

from fastapi import FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Try to import SSE, fallback if not available
try:
    from sse_starlette.sse import EventSourceResponse
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False
    print("[Warning] sse-starlette not installed. SSE endpoint will be disabled.")
    # Create a dummy EventSourceResponse
    class EventSourceResponse:
        def __init__(self, generator):
            self.generator = generator
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
import traceback
import json
import asyncio
from backend.graph import app_graph
from backend.memory.storage import memory_storage
from backend.observability import observability
from backend.context import window_context

app = FastAPI(
    title="Collaborative Agent System",
    description="Intelligent Support & Incident Co-Pilot System",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Ticket(BaseModel):
    ticket: str = Field(..., min_length=1, description="Ticket or query text")

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    outcome: Optional[str] = None
    metadata: Optional[dict] = None

@app.post("/ticket")
def run(ticket: Ticket):
    """Process a ticket through the agent system."""
    try:
        task_id = str(uuid.uuid4())
        initial_state = {
            "ticket": ticket.ticket,
            "input": ticket.ticket,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat()
        }
        print(f"[API] Processing ticket: {ticket.ticket[:50]}...")
        
        # Log ticket processing start
        observability.log_agent_execution("System", initial_state, "ticket_received")
        
        # Apply context windowing before processing
        initial_state = window_context(initial_state)
        
        result = app_graph.invoke(initial_state)
        
        # Log completion
        if result:
            observability.log_agent_execution("System", result, "ticket_processed")
        print(f"[API] Graph execution complete. Result type: {type(result)}")
        if result:
            print(f"[API] Result keys: {list(result.keys())}")
            print(f"[API] Confidence in result: {result.get('confidence')}")
            print(f"[API] Action in result: {result.get('action')}")
            print(f"[API] Reasoning in result: {result.get('reasoning')}")
        
        # Convert result to dict if it's a State object
        if result is None:
            print("[API] WARNING: Graph returned None!")
            return {
                "error": "Graph execution returned no result",
                "ticket": ticket.ticket
            }
        
        # Ensure result is a dict
        if isinstance(result, dict):
            # Filter out internal/langgraph keys and ensure JSON-serializable
            # Get confidence - handle 0.0 as valid value
            confidence_value = result.get("confidence")
            if confidence_value is None:
                confidence_value = 0.0  # Default if not set
            
            response_data = {
                "ticket": result.get("ticket", ticket.ticket),
                "priority": result.get("priority", "UNKNOWN"),
                "action": result.get("action", "UNKNOWN"),
                "response": result.get("response", ""),
                "confidence": float(confidence_value),
                "task_id": result.get("task_id", task_id),
                "timestamp": result.get("timestamp", datetime.now().isoformat()),
            }
            
            # Add optional fields if they exist
            if "retrieved_docs" in result:
                response_data["retrieved_docs"] = result["retrieved_docs"][:3]  # Limit to 3
            if "correlation" in result:
                # Remove duplicates from correlation
                correlation = result["correlation"]
                if isinstance(correlation, list):
                    response_data["correlation"] = list(dict.fromkeys(correlation))  # Preserve order, remove dupes
                else:
                    response_data["correlation"] = correlation
            if "past_incidents" in result:
                past_incidents = result["past_incidents"]
                if isinstance(past_incidents, list):
                    response_data["past_incidents"] = list(dict.fromkeys(past_incidents))[:5]  # Remove dupes, limit to 5
                else:
                    response_data["past_incidents"] = past_incidents[:5] if isinstance(past_incidents, list) else []
            if "escalation_reason" in result:
                response_data["escalation_reason"] = result["escalation_reason"]
            
            print(f"[API] Returning response with priority: {response_data.get('priority')}, action: {response_data.get('action')}")
            return response_data
        else:
            # If it's not a dict, try to convert it
            print(f"[API] Result is not a dict, converting... Type: {type(result)}")
            return {
                "ticket": ticket.ticket,
                "raw_result": str(result),
                "error": "Unexpected result type from graph"
            }
    except Exception as e:
        print(f"[Error] Failed to process ticket: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process ticket: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agent-system"}

# WebSocket endpoint for real-time agent streaming
@app.websocket("/ws/agent-stream")
async def websocket_agent_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time agent event streaming."""
    await websocket.accept()
    try:
        while True:
            # Send recent events
            events = observability.get_recent_events(limit=50)
            await websocket.send_json({
                "type": "events",
                "data": events,
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(1)  # Send updates every second
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")

# SSE endpoint for real-time agent streaming
@app.get("/sse/agent-stream")
async def sse_agent_stream():
    """Server-Sent Events endpoint for real-time agent event streaming."""
    if not SSE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SSE not available. Install sse-starlette: pip install sse-starlette"
        )
    
    async def event_generator():
        last_count = 0
        event_ids_seen = set()  # Track which events we've already sent
        
        while True:
            events = observability.get_recent_events(limit=100)
            if len(events) > last_count:
                # New events available
                new_events = events[last_count:]
                for event in new_events:
                    # Create unique ID for this event to avoid duplicates
                    event_id = f"{event.get('timestamp', '')}-{event.get('agent_name', 'unknown')}-{event.get('type', 'unknown')}"
                    if event_id not in event_ids_seen:
                        event_ids_seen.add(event_id)
                        # Format event for frontend - include all relevant fields
                        formatted_event = {
                            "type": event.get("type", "agent_event"),
                            "agent_name": event.get("agent_name", "System"),
                            "action": event.get("action", ""),
                            "decision": event.get("decision", ""),
                            "tool_name": event.get("tool_name", ""),
                            "reasoning": event.get("reasoning", ""),
                            "timestamp": event.get("timestamp", datetime.now().isoformat()),
                            "data_used": event.get("data_used", {}),
                            "state_snapshot": event.get("state_snapshot", {})
                        }
                        # SSE format: yield dict with 'data' as JSON string
                        yield {
                            "event": "agent_event",
                            "data": json.dumps(formatted_event, default=str)
                        }
                last_count = len(events)
            await asyncio.sleep(0.2)  # Check every 200ms for faster updates
    
    return EventSourceResponse(event_generator())

# Observability endpoints
@app.get("/observability/events")
def get_observability_events(limit: int = 100):
    """Get recent observability events."""
    return {
        "events": observability.get_recent_events(limit=limit),
        "total": len(observability.agent_events)
    }

@app.get("/observability/tool-calls")
def get_tool_calls(agent_name: Optional[str] = None):
    """Get tool call history."""
    return {
        "tool_calls": observability.get_tool_calls(agent_name=agent_name),
        "total": len(observability.tool_calls)
    }

# Memory Management Endpoints
@app.get("/memory/episodic")
def get_episodic_memory(limit: Optional[int] = None):
    """Get episodic memories."""
    return memory_storage.get_episodic_memory(limit=limit)

@app.get("/memory/episodic/{memory_id}")
def get_episodic_memory_by_id(memory_id: int):
    """Get specific episodic memory."""
    try:
        memories = memory_storage.get_episodic_memory()
        for m in memories:
            if m.get("id") == memory_id:
                return m
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with id {memory_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve memory: {str(e)}"
        )

@app.put("/memory/episodic/{memory_id}")
def update_episodic_memory(memory_id: int, update: MemoryUpdate):
    """Update episodic memory."""
    updates = {}
    if update.content:
        updates["incident"] = update.content
    if update.outcome:
        updates["outcome"] = update.outcome
    if update.metadata:
        updates["metadata"] = update.metadata
    
    success = memory_storage.update_episodic_memory(memory_id, updates)
    if success:
        return {"success": True, "message": "Memory updated"}
    return {"success": False, "message": "Memory not found"}

@app.delete("/memory/episodic/{memory_id}")
def delete_episodic_memory(memory_id: int):
    """Delete episodic memory."""
    memory_storage.delete_episodic_memory(memory_id)
    return {"success": True, "message": "Memory deleted"}

@app.get("/memory/semantic")
def get_semantic_memory(doc_type: Optional[str] = None):
    """Get semantic memories."""
    return memory_storage.get_semantic_memory(doc_type=doc_type)

@app.delete("/memory/semantic/{memory_id}")
def delete_semantic_memory(memory_id: int):
    """Delete semantic memory."""
    memory_storage.delete_semantic_memory(memory_id)
    return {"success": True, "message": "Memory deleted"}

@app.get("/memory/working")
def get_working_memory(task_id: Optional[str] = None):
    """Get working memory."""
    return memory_storage.get_working_memory(task_id=task_id)

