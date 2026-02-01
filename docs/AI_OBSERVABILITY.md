# AI Observability Guide

## Overview

The AI Observability system tracks all AI-related operations including:
- **Token Usage**: Input/output tokens for LLM calls
- **Cost Tracking**: Real-time cost calculation based on model pricing
- **Latency Metrics**: Response time for all AI operations
- **Performance Analytics**: Success rates, error tracking, model performance
- **Agent-Level Metrics**: Track which agents use the most AI resources
- **Operation-Level Metrics**: Track costs by operation type (e.g., response_generation, intent_classification)

## Features

### 1. Automatic LLM Tracking
When using `ObservableChatOpenAI`, all calls are automatically tracked:
- Token usage (prompt + completion)
- Cost calculation
- Latency measurement
- Success/failure status
- Prompt and response previews

### 2. Embedding Tracking
Track embedding API calls:
- Input tokens
- Cost per call
- Latency
- Operation type

### 3. Aggregated Metrics
- Daily summaries
- Model-level breakdowns
- Agent-level breakdowns
- Operation-level breakdowns
- Error rates
- Average latency

## Usage

### Option 1: Use ObservableChatOpenAI (Recommended)

Replace your existing `ChatOpenAI` calls:

**Before:**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=config.OPENAI_API_KEY
)
```

**After:**
```python
from backend.observability import create_observable_llm

llm = create_observable_llm(
    agent_name="ResponseAgent",
    operation="response_generation",
    task_id=state.get("task_id"),
    model="gpt-3.5-turbo",
    temperature=0.7
)
```

### Option 2: Manual Tracking

If you need to track custom operations:

```python
from backend.observability import ai_metrics
import time

start_time = time.time()
# ... your AI operation ...
latency_ms = (time.time() - start_time) * 1000

# Track LLM call
ai_metrics.track_llm_call(
    model="gpt-3.5-turbo",
    agent_name="MyAgent",
    operation="custom_operation",
    prompt_tokens=100,
    completion_tokens=50,
    latency_ms=latency_ms,
    task_id="task_123"
)

# Track embedding call
ai_metrics.track_embedding_call(
    model="text-embedding-3-small",
    operation="document_embedding",
    input_tokens=500,
    latency_ms=latency_ms
)
```

## API Endpoints

### Get AI Metrics Summary
```bash
GET /observability/ai-metrics/summary?days=7
```

Returns:
- Total LLM calls
- Total embedding calls
- Total tokens used
- Total cost (USD)
- Average latency
- Error rate
- Breakdowns by model, agent, and operation
- Daily breakdown

### Get Recent LLM Calls
```bash
GET /observability/ai-metrics/llm-calls?limit=100&task_id=task_123
```

Returns list of recent LLM calls with:
- Model used
- Agent name
- Operation type
- Token usage
- Cost
- Latency
- Success status
- Prompt/response previews

### Get Recent Embedding Calls
```bash
GET /observability/ai-metrics/embedding-calls?limit=100
```

### Export Metrics
```bash
GET /observability/ai-metrics/export?days=30
```

Returns complete metrics data for export/analysis.

## Example Response

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
    }
  ]
}
```

## Integration with Existing Code

### Update Response Agent

In `backend/agents/response.py`:

```python
# Replace this:
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo", ...)

# With this:
from backend.observability import create_observable_llm
llm = create_observable_llm(
    agent_name="ResponseAgent",
    operation="response_generation",
    task_id=state.get("task_id"),
    model="gpt-3.5-turbo",
    ...
)
```

### Update Intent Agent

In `backend/agents/intent.py`:

```python
from backend.observability import create_observable_llm

llm = create_observable_llm(
    agent_name="IntentAgent",
    operation="intent_classification",
    task_id=state.get("task_id"),
    model="gpt-3.5-turbo",
    temperature=0
)
```

### Update Planner Agent

In `backend/agents/planner.py`:

```python
from backend.observability import create_observable_llm

llm = create_observable_llm(
    agent_name="PlannerAgent",
    operation="execution_planning",
    task_id=None,  # Planning happens before task_id is set
    model="gpt-3.5-turbo",
    temperature=0
)
```

## Cost Tracking

The system automatically calculates costs based on current OpenAI pricing:

- **gpt-3.5-turbo**: $0.50/1M input, $1.50/1M output
- **gpt-4**: $30/1M input, $60/1M output
- **gpt-4-turbo**: $10/1M input, $30/1M output
- **text-embedding-3-small**: $0.20/1M tokens
- **text-embedding-3-large**: $1.30/1M tokens

Prices are updated in `backend/observability/ai_metrics.py` - update `PRICING` dict as needed.

## Benefits

1. **Cost Visibility**: Know exactly how much each agent/operation costs
2. **Performance Monitoring**: Track latency and identify slow operations
3. **Error Tracking**: Monitor AI call failures
4. **Optimization**: Identify expensive operations for optimization
5. **Budgeting**: Forecast costs based on usage patterns
6. **Debugging**: See prompt/response previews for failed calls

## Next Steps

1. Update agents to use `create_observable_llm()` instead of `ChatOpenAI`
2. Monitor metrics via API endpoints
3. Set up alerts for high costs or error rates
4. Export metrics for analysis and reporting

