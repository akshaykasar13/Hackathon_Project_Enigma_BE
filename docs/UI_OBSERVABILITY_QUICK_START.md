# Quick Start Guide: Observability UI Integration

## 5-Minute Integration

### Step 1: Test API Connection

```javascript
// Test if API is accessible
fetch('http://localhost:8000/observability/ai-metrics/summary?days=1')
  .then(res => res.json())
  .then(data => {
    console.log('✅ API is working!');
    console.log('Total cost:', data.total_cost_usd);
  })
  .catch(err => {
    console.error('❌ API connection failed:', err);
  });
```

### Step 2: Display Key Metrics

```javascript
// Get and display key metrics
async function loadMetrics() {
  const summary = await fetch('/observability/ai-metrics/summary?days=1')
    .then(res => res.json());
  
  // Display in your UI
  document.getElementById('total-cost').textContent = 
    `$${summary.total_cost_usd.toFixed(2)}`;
  document.getElementById('total-tokens').textContent = 
    summary.total_tokens.toLocaleString();
  document.getElementById('total-calls').textContent = 
    summary.total_llm_calls + summary.total_embedding_calls;
}
```

### Step 3: Show Recent Activity

```javascript
// Get recent events
async function loadRecentActivity() {
  const events = await fetch('/observability/events?limit=10')
    .then(res => res.json());
  
  const activityList = document.getElementById('activity-list');
  events.events.forEach(event => {
    const item = document.createElement('div');
    item.innerHTML = `
      <strong>${event.agent_name}</strong>: ${event.action}
      <small>${new Date(event.timestamp).toLocaleTimeString()}</small>
    `;
    activityList.appendChild(item);
  });
}
```

### Step 4: Auto-Refresh (Optional)

```javascript
// Refresh every 5 seconds
setInterval(() => {
  loadMetrics();
  loadRecentActivity();
}, 5000);
```

---

## Essential Endpoints

| Endpoint | Purpose | Refresh Rate |
|----------|---------|--------------|
| `/observability/ai-metrics/summary?days=1` | Dashboard summary | Every 5-10s |
| `/observability/events?limit=20` | Recent activity | Every 2-3s |
| `/observability/ai-metrics/llm-calls?limit=10` | Recent LLM calls | On demand |
| `/observability/trace/{task_id}` | Task execution trace | When viewing task |

---

## React Example

```jsx
import { useState, useEffect } from 'react';

function ObservabilityDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Load metrics
    fetch('/observability/ai-metrics/summary?days=1')
      .then(res => res.json())
      .then(setMetrics);

    // Load events
    fetch('/observability/events?limit=20')
      .then(res => res.json())
      .then(data => setEvents(data.events));

    // Auto-refresh every 5 seconds
    const interval = setInterval(() => {
      fetch('/observability/ai-metrics/summary?days=1')
        .then(res => res.json())
        .then(setMetrics);
      
      fetch('/observability/events?limit=20')
        .then(res => res.json())
        .then(data => setEvents(data.events));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!metrics) return <div>Loading...</div>;

  return (
    <div>
      <h1>AI Observability Dashboard</h1>
      
      <div className="metrics">
        <div className="metric">
          <label>Total Cost</label>
          <value>${metrics.total_cost_usd.toFixed(2)}</value>
        </div>
        <div className="metric">
          <label>Total Tokens</label>
          <value>{metrics.total_tokens.toLocaleString()}</value>
        </div>
        <div className="metric">
          <label>Total Calls</label>
          <value>{metrics.total_llm_calls + metrics.total_embedding_calls}</value>
        </div>
      </div>

      <div className="activity">
        <h2>Recent Activity</h2>
        {events.map((event, i) => (
          <div key={i} className="activity-item">
            <strong>{event.agent_name}</strong>: {event.action}
            <small>{new Date(event.timestamp).toLocaleTimeString()}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Vue Example

```vue
<template>
  <div class="observability-dashboard">
    <h1>AI Observability Dashboard</h1>
    
    <div class="metrics">
      <div class="metric">
        <label>Total Cost</label>
        <value>${{ metrics?.total_cost_usd?.toFixed(2) || '0.00' }}</value>
      </div>
      <div class="metric">
        <label>Total Tokens</label>
        <value>{{ metrics?.total_tokens?.toLocaleString() || '0' }}</value>
      </div>
    </div>

    <div class="activity">
      <h2>Recent Activity</h2>
      <div v-for="event in events" :key="event.timestamp" class="activity-item">
        <strong>{{ event.agent_name }}</strong>: {{ event.action }}
        <small>{{ formatTime(event.timestamp) }}</small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      metrics: null,
      events: []
    };
  },
  mounted() {
    this.loadData();
    setInterval(this.loadData, 5000);
  },
  methods: {
    async loadData() {
      const [metricsRes, eventsRes] = await Promise.all([
        fetch('/observability/ai-metrics/summary?days=1'),
        fetch('/observability/events?limit=20')
      ]);
      
      this.metrics = await metricsRes.json();
      const eventsData = await eventsRes.json();
      this.events = eventsData.events;
    },
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString();
    }
  }
};
</script>
```

---

## Key Data Points to Display

### Dashboard Summary
- **Total Cost**: `summary.total_cost_usd`
- **Total Tokens**: `summary.total_tokens`
- **Total Calls**: `summary.total_llm_calls + summary.total_embedding_calls`
- **Average Latency**: `summary.avg_latency_ms`
- **Error Rate**: `summary.error_rate`

### By Agent Breakdown
- Loop through `summary.by_agent` to show:
  - Agent name
  - Number of calls
  - Tokens used
  - Cost incurred
  - Percentage of total cost

### Daily Trends
- Use `summary.daily_breakdown` array to show:
  - Daily cost trend (line chart)
  - Daily token usage (bar chart)
  - Daily error rate (line chart)

---

## Common Use Cases

### 1. Cost Monitoring
```javascript
// Alert if cost exceeds threshold
const summary = await fetch('/observability/ai-metrics/summary?days=1')
  .then(res => res.json());

if (summary.total_cost_usd > 50) {
  alert('⚠️ Daily cost exceeds $50!');
}
```

### 2. Performance Monitoring
```javascript
// Alert if latency is high
if (summary.avg_latency_ms > 5000) {
  alert('⚠️ High latency detected!');
}
```

### 3. Error Tracking
```javascript
// Alert if error rate is high
if (summary.error_rate > 0.1) {
  alert('⚠️ High error rate detected!');
}
```

---

## Next Steps

1. ✅ Test API connection
2. ✅ Display key metrics
3. ✅ Show recent activity
4. 📊 Add charts (use Chart.js, D3.js, or your preferred library)
5. 🔄 Implement auto-refresh
6. 📱 Make it responsive
7. 🎨 Style it to match your design system

For complete API documentation, see `docs/UI_OBSERVABILITY_API.md`.

