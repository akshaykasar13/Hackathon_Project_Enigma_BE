# Observability API Documentation for UI Integration

## Overview

This document provides complete API documentation for integrating observability features into the UI. The observability system tracks:
- **Agent Execution**: Which agents ran, when, and their decisions
- **Tool Calls**: What tools were called and their results
- **AI Metrics**: Token usage, costs, latency for all LLM calls
- **Execution Traces**: Complete request-to-response flow

---

## Base URL

```
http://localhost:8000
```

For production, replace with your production URL.

---

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible.

---

## Endpoints

### 1. Get Observability Events

Get recent observability events (agent executions, tool calls, decisions).

**Endpoint:** `GET /observability/events`

**Query Parameters:**
- `limit` (optional, default: 100): Number of events to return
- `task_id` (optional): Filter events by specific task ID

**Response:**
```json
{
  "events": [
    {
      "type": "agent_execution",
      "timestamp": "2024-01-15T10:30:45.123456",
      "agent_name": "IntentAgent",
      "task_id": "task_123",
      "action": "classified_high",
      "reasoning": "currency-related failures impacting multiple users"
    },
    {
      "type": "tool_call_start",
      "timestamp": "2024-01-15T10:30:44.123456",
      "tool_name": "intent_classification",
      "agent_name": "IntentAgent",
      "task_id": "task_123",
      "inputs": {
        "ticket": "Payment failed for user..."
      }
    }
  ],
  "total": 1250
}
```

**Example Request:**
```javascript
// Get last 50 events
fetch('http://localhost:8000/observability/events?limit=50')
  .then(res => res.json())
  .then(data => console.log(data));

// Get events for specific task
fetch('http://localhost:8000/observability/events?task_id=task_123')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 2. Get Tool Calls

Get history of tool calls with execution times and results.

**Endpoint:** `GET /observability/tool-calls`

**Query Parameters:**
- `agent_name` (optional): Filter by agent name (e.g., "ResponseAgent", "IntentAgent")
- `task_id` (optional): Filter by task ID

**Response:**
```json
{
  "tool_calls": [
    {
      "tool_name": "response_generation",
      "agent_name": "ResponseAgent",
      "task_id": "task_123",
      "inputs": {
        "ticket": "Payment failed...",
        "method": "LLM"
      },
      "start_time": "2024-01-15T10:30:45.123456",
      "end_time": "2024-01-15T10:30:46.234567",
      "result": "{\"response_length\": 150}",
      "error": null,
      "execution_time_ms": 1111.11,
      "status": "success"
    }
  ],
  "total": 500
}
```

**Example Request:**
```javascript
// Get all tool calls
fetch('http://localhost:8000/observability/tool-calls')
  .then(res => res.json())
  .then(data => console.log(data));

// Get tool calls for specific agent
fetch('http://localhost:8000/observability/tool-calls?agent_name=ResponseAgent')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 3. Get Execution Trace

Get complete execution trace for a specific task (request-to-response flow).

**Endpoint:** `GET /observability/trace/{task_id}`

**Path Parameters:**
- `task_id`: The task ID to get trace for

**Response:**
```json
{
  "task_id": "task_123",
  "execution_trace": [
    {
      "agent": "IngestionAgent",
      "action": "ticket_ingested",
      "timestamp": "2024-01-15T10:30:40.000000"
    },
    {
      "agent": "IntentAgent",
      "action": "classified_high",
      "timestamp": "2024-01-15T10:30:41.000000"
    },
    {
      "agent": "PlannerAgent",
      "action": "strategy_planned",
      "timestamp": "2024-01-15T10:30:42.000000"
    }
  ],
  "agent_events": [
    {
      "type": "agent_execution",
      "agent_name": "IntentAgent",
      "action": "classified_high",
      "reasoning": "currency-related failures"
    }
  ]
}
```

**Example Request:**
```javascript
fetch('http://localhost:8000/observability/trace/task_123')
  .then(res => res.json())
  .then(data => {
    console.log('Execution trace:', data.execution_trace);
    console.log('Agent events:', data.agent_events);
  });
```

---

## AI Metrics Endpoints

### 4. Get AI Metrics Summary

Get aggregated AI metrics (tokens, costs, latency) for the last N days.

**Endpoint:** `GET /observability/ai-metrics/summary`

**Query Parameters:**
- `days` (optional, default: 1): Number of days to include in summary

**Response:**
```json
{
  "period_days": 7,
  "total_llm_calls": 1250,
  "total_embedding_calls": 3400,
  "total_tokens": 245000,
  "total_cost_usd": 12.45,
  "avg_latency_ms": 1250.5,
  "error_rate": 0.02,
  "by_model": {
    "gpt-3.5-turbo": {
      "calls": 1200,
      "tokens": 200000,
      "cost": 10.00
    },
    "text-embedding-3-small": {
      "calls": 3400,
      "tokens": 45000,
      "cost": 2.45
    }
  },
  "by_agent": {
    "ResponseAgent": {
      "calls": 500,
      "tokens": 100000,
      "cost": 5.00
    },
    "IntentAgent": {
      "calls": 300,
      "tokens": 50000,
      "cost": 2.50
    },
    "PlannerAgent": {
      "calls": 200,
      "tokens": 30000,
      "cost": 1.50
    },
    "ReasoningAgent": {
      "calls": 150,
      "tokens": 15000,
      "cost": 0.75
    },
    "GuardrailsAgent": {
      "calls": 100,
      "tokens": 5000,
      "cost": 0.25
    }
  },
  "by_operation": {
    "response_generation": {
      "calls": 500,
      "tokens": 100000,
      "cost": 5.00
    },
    "intent_classification": {
      "calls": 300,
      "tokens": 50000,
      "cost": 2.50
    },
    "execution_planning": {
      "calls": 200,
      "tokens": 30000,
      "cost": 1.50
    },
    "root_cause_analysis": {
      "calls": 150,
      "tokens": 15000,
      "cost": 0.75
    },
    "safety_check": {
      "calls": 100,
      "tokens": 5000,
      "cost": 0.25
    }
  },
  "daily_breakdown": [
    {
      "date": "2024-01-15",
      "llm_calls": 200,
      "embedding_calls": 500,
      "total_tokens": 35000,
      "cost_usd": 1.75,
      "errors": 2,
      "error_rate": 0.003
    },
    {
      "date": "2024-01-14",
      "llm_calls": 180,
      "embedding_calls": 480,
      "total_tokens": 32000,
      "cost_usd": 1.60,
      "errors": 1,
      "error_rate": 0.001
    }
  ]
}
```

**Example Request:**
```javascript
// Get summary for last 7 days
fetch('http://localhost:8000/observability/ai-metrics/summary?days=7')
  .then(res => res.json())
  .then(data => {
    console.log('Total cost:', data.total_cost_usd);
    console.log('By agent:', data.by_agent);
    console.log('Daily breakdown:', data.daily_breakdown);
  });
```

---

### 5. Get Recent LLM Calls

Get detailed information about recent LLM API calls.

**Endpoint:** `GET /observability/ai-metrics/llm-calls`

**Query Parameters:**
- `limit` (optional, default: 100): Number of calls to return
- `task_id` (optional): Filter by task ID

**Response:**
```json
{
  "llm_calls": [
    {
      "call_id": "call_1705312245123_1",
      "model": "gpt-3.5-turbo",
      "agent_name": "ResponseAgent",
      "operation": "response_generation",
      "task_id": "task_123",
      "prompt_tokens": 500,
      "completion_tokens": 150,
      "total_tokens": 650,
      "cost_usd": 0.000975,
      "latency_ms": 1250.5,
      "timestamp": "2024-01-15T10:30:45.123456",
      "success": true,
      "error": null,
      "prompt_preview": "Generate a response for the following ticket...",
      "response_preview": "Thank you for reporting this issue..."
    }
  ],
  "total": 1250
}
```

**Example Request:**
```javascript
// Get last 50 LLM calls
fetch('http://localhost:8000/observability/ai-metrics/llm-calls?limit=50')
  .then(res => res.json())
  .then(data => {
    data.llm_calls.forEach(call => {
      console.log(`${call.agent_name}: ${call.operation} - ${call.total_tokens} tokens, $${call.cost_usd}`);
    });
  });

// Get LLM calls for specific task
fetch('http://localhost:8000/observability/ai-metrics/llm-calls?task_id=task_123')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 6. Get Recent Embedding Calls

Get detailed information about recent embedding API calls.

**Endpoint:** `GET /observability/ai-metrics/embedding-calls`

**Query Parameters:**
- `limit` (optional, default: 100): Number of calls to return

**Response:**
```json
{
  "embedding_calls": [
    {
      "call_id": "call_1705312245123_2",
      "model": "text-embedding-3-small",
      "operation": "document_embedding",
      "input_tokens": 1000,
      "cost_usd": 0.0002,
      "latency_ms": 250.5,
      "timestamp": "2024-01-15T10:30:40.123456",
      "success": true,
      "error": null
    }
  ],
  "total": 3400
}
```

**Example Request:**
```javascript
fetch('http://localhost:8000/observability/ai-metrics/embedding-calls?limit=50')
  .then(res => res.json())
  .then(data => {
    console.log('Total embedding calls:', data.total);
    console.log('Recent calls:', data.embedding_calls);
  });
```

---

### 7. Export AI Metrics

Export complete AI metrics data for analysis.

**Endpoint:** `GET /observability/ai-metrics/export`

**Query Parameters:**
- `days` (optional, default: 30): Number of days to export

**Response:**
```json
{
  "summary": {
    // Same as /summary endpoint
  },
  "recent_llm_calls": [
    // Array of LLM calls (up to 1000)
  ],
  "recent_embedding_calls": [
    // Array of embedding calls (up to 1000)
  ],
  "exported_at": "2024-01-15T10:30:45.123456"
}
```

**Example Request:**
```javascript
fetch('http://localhost:8000/observability/ai-metrics/export?days=30')
  .then(res => res.json())
  .then(data => {
    // Export to file or process data
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-metrics-export-${new Date().toISOString()}.json`;
    a.click();
  });
```

---

## UI Integration Examples

### Real-Time Dashboard

```javascript
// Fetch data every 5 seconds for real-time dashboard
setInterval(async () => {
  // Get summary
  const summary = await fetch('/observability/ai-metrics/summary?days=1')
    .then(res => res.json());
  
  // Get recent events
  const events = await fetch('/observability/events?limit=20')
    .then(res => res.json());
  
  // Update UI
  updateDashboard(summary, events);
}, 5000);

function updateDashboard(summary, events) {
  // Update cost display
  document.getElementById('total-cost').textContent = `$${summary.total_cost_usd.toFixed(2)}`;
  
  // Update token usage
  document.getElementById('total-tokens').textContent = summary.total_tokens.toLocaleString();
  
  // Update recent activity
  const activityList = document.getElementById('recent-activity');
  events.events.slice(0, 10).forEach(event => {
    const item = document.createElement('li');
    item.textContent = `${event.agent_name}: ${event.action}`;
    activityList.appendChild(item);
  });
}
```

### Cost Breakdown Chart

```javascript
// Get summary for last 7 days
const summary = await fetch('/observability/ai-metrics/summary?days=7')
  .then(res => res.json());

// Prepare data for chart (using Chart.js example)
const chartData = {
  labels: Object.keys(summary.by_agent),
  datasets: [{
    label: 'Cost by Agent',
    data: Object.values(summary.by_agent).map(agent => agent.cost),
    backgroundColor: [
      'rgba(255, 99, 132, 0.6)',
      'rgba(54, 162, 235, 0.6)',
      'rgba(255, 206, 86, 0.6)',
      'rgba(75, 192, 192, 0.6)',
      'rgba(153, 102, 255, 0.6)'
    ]
  }]
};

// Render chart
new Chart(document.getElementById('cost-chart'), {
  type: 'pie',
  data: chartData
});
```

### Execution Timeline

```javascript
// Get execution trace for a task
async function renderExecutionTimeline(taskId) {
  const trace = await fetch(`/observability/trace/${taskId}`)
    .then(res => res.json());
  
  const timeline = document.getElementById('execution-timeline');
  
  trace.execution_trace.forEach((step, index) => {
    const stepElement = document.createElement('div');
    stepElement.className = 'timeline-step';
    stepElement.innerHTML = `
      <div class="step-number">${index + 1}</div>
      <div class="step-agent">${step.agent}</div>
      <div class="step-action">${step.action}</div>
      <div class="step-time">${new Date(step.timestamp).toLocaleTimeString()}</div>
    `;
    timeline.appendChild(stepElement);
  });
}
```

### Agent Performance Table

```javascript
// Display agent performance metrics
async function renderAgentPerformance() {
  const summary = await fetch('/observability/ai-metrics/summary?days=7')
    .then(res => res.json());
  
  const table = document.getElementById('agent-performance-table');
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  
  Object.entries(summary.by_agent).forEach(([agent, metrics]) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${agent}</td>
      <td>${metrics.calls}</td>
      <td>${metrics.tokens.toLocaleString()}</td>
      <td>$${metrics.cost.toFixed(2)}</td>
      <td>${(metrics.cost / summary.total_cost_usd * 100).toFixed(1)}%</td>
    `;
    tbody.appendChild(row);
  });
}
```

### Daily Cost Trend

```javascript
// Get daily breakdown for trend chart
const summary = await fetch('/observability/ai-metrics/summary?days=30')
  .then(res => res.json());

const trendData = {
  labels: summary.daily_breakdown.map(d => d.date),
  datasets: [{
    label: 'Daily Cost (USD)',
    data: summary.daily_breakdown.map(d => d.cost_usd),
    borderColor: 'rgb(75, 192, 192)',
    tension: 0.1
  }]
};

new Chart(document.getElementById('cost-trend-chart'), {
  type: 'line',
  data: trendData,
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});
```

---

## Event Types

### Agent Execution Events
```json
{
  "type": "agent_execution",
  "agent_name": "IntentAgent",
  "action": "classified_high",
  "reasoning": "currency-related failures impacting multiple users",
  "timestamp": "2024-01-15T10:30:45.123456",
  "task_id": "task_123"
}
```

### Tool Call Events
```json
{
  "type": "tool_call_start",
  "tool_name": "intent_classification",
  "agent_name": "IntentAgent",
  "timestamp": "2024-01-15T10:30:44.123456",
  "task_id": "task_123",
  "inputs": {
    "ticket": "Payment failed..."
  }
}
```

### Decision Events
```json
{
  "type": "decision",
  "agent_name": "IntentAgent",
  "decision": "Classified as HIGH",
  "reasoning": "currency-related failures",
  "timestamp": "2024-01-15T10:30:45.123456",
  "task_id": "task_123",
  "data_used": {
    "ticket_text": "Payment failed...",
    "categories": ["billing", "data_issue"]
  }
}
```

---

## Agent Names

Available agent names for filtering:
- `IngestionAgent`
- `IntentAgent`
- `PlannerAgent`
- `RetrievalAgent`
- `MemoryAgent`
- `ReasoningAgent`
- `ResponseAgent`
- `GuardrailsAgent`

---

## Operation Types

Available operation types for AI metrics:
- `response_generation`
- `intent_classification`
- `execution_planning`
- `root_cause_analysis`
- `safety_check`
- `document_embedding`
- `memory_search`

---

## Error Handling

All endpoints return standard HTTP status codes:
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Example Error Response:**
```json
{
  "detail": "Task ID not found"
}
```

**Error Handling Example:**
```javascript
async function fetchWithErrorHandling(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    // Show error message to user
    return null;
  }
}
```

---

## Polling Recommendations

For real-time updates, we recommend:

1. **Dashboard Summary**: Poll every 5-10 seconds
   ```javascript
   setInterval(() => {
     fetch('/observability/ai-metrics/summary?days=1')
       .then(res => res.json())
       .then(updateDashboard);
   }, 5000);
   ```

2. **Recent Events**: Poll every 2-3 seconds
   ```javascript
   setInterval(() => {
     fetch('/observability/events?limit=20')
       .then(res => res.json())
       .then(updateActivityFeed);
   }, 2000);
   ```

3. **Task-Specific**: Poll only when viewing a specific task
   ```javascript
   // Only poll when task detail view is open
   if (currentTaskId) {
     setInterval(() => {
       fetch(`/observability/trace/${currentTaskId}`)
         .then(res => res.json())
         .then(updateTaskView);
     }, 1000);
   }
   ```

---

## Sample Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  AI Observability Dashboard                             │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Total    │  │ Total    │  │ Avg      │  │ Error    ││
│  │ Cost     │  │ Tokens   │  │ Latency  │  │ Rate     ││
│  │ $12.45   │  │ 245,000  │  │ 1,250ms  │  │ 2.0%     ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
├─────────────────────────────────────────────────────────┤
│  Cost by Agent (Pie Chart)                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  [Pie Chart: ResponseAgent, IntentAgent, etc.]   │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  Daily Cost Trend (Line Chart)                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  [Line Chart showing daily costs over time]       │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  Recent Activity                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  • IntentAgent: classified_high                  │  │
│  │  • ResponseAgent: response_generated              │  │
│  │  • ReasoningAgent: analysis_complete              │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Additional Resources

- **Backend API Docs**: See `backend/main.py` for all available endpoints
- **AI Observability Guide**: See `docs/AI_OBSERVABILITY.md` for implementation details
- **Test Script**: Use `test_ai_metrics.ps1` to test endpoints

---

## Support

For questions or issues with the API, contact the backend team or check the backend logs at `backend/logs/agent_system.log`.

