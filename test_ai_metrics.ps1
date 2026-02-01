# Test AI Metrics API Endpoints

Write-Host "`n=== Testing AI Metrics API Endpoints ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Summary
Write-Host "1. Testing /observability/ai-metrics/summary" -ForegroundColor Yellow
try {
    $summary = Invoke-RestMethod -Uri "http://localhost:8000/observability/ai-metrics/summary?days=1" -Method Get
    Write-Host "   ✅ Success!" -ForegroundColor Green
    Write-Host "   Total LLM Calls: $($summary.total_llm_calls)" -ForegroundColor White
    Write-Host "   Total Embedding Calls: $($summary.total_embedding_calls)" -ForegroundColor White
    Write-Host "   Total Tokens: $($summary.total_tokens)" -ForegroundColor White
    Write-Host "   Total Cost: `$$($summary.total_cost_usd.ToString('F6'))" -ForegroundColor White
    Write-Host "   Avg Latency: $($summary.avg_latency_ms.ToString('F2'))ms" -ForegroundColor White
    Write-Host "   Error Rate: $($summary.error_rate.ToString('P2'))" -ForegroundColor White
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: LLM Calls
Write-Host "2. Testing /observability/ai-metrics/llm-calls" -ForegroundColor Yellow
try {
    $llmCalls = Invoke-RestMethod -Uri "http://localhost:8000/observability/ai-metrics/llm-calls?limit=5" -Method Get
    Write-Host "   ✅ Success!" -ForegroundColor Green
    Write-Host "   Total LLM Calls Stored: $($llmCalls.total)" -ForegroundColor White
    Write-Host "   Recent Calls Returned: $($llmCalls.llm_calls.Count)" -ForegroundColor White
    if ($llmCalls.llm_calls.Count -gt 0) {
        $latest = $llmCalls.llm_calls[0]
        Write-Host "   Latest Call:" -ForegroundColor Cyan
        Write-Host "     - Agent: $($latest.agent_name)" -ForegroundColor White
        Write-Host "     - Operation: $($latest.operation)" -ForegroundColor White
        Write-Host "     - Model: $($latest.model)" -ForegroundColor White
        Write-Host "     - Tokens: $($latest.total_tokens) ($($latest.prompt_tokens)+$($latest.completion_tokens))" -ForegroundColor White
        Write-Host "     - Cost: `$$($latest.cost_usd.ToString('F6'))" -ForegroundColor White
        Write-Host "     - Latency: $($latest.latency_ms.ToString('F2'))ms" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Embedding Calls
Write-Host "3. Testing /observability/ai-metrics/embedding-calls" -ForegroundColor Yellow
try {
    $embeddings = Invoke-RestMethod -Uri "http://localhost:8000/observability/ai-metrics/embedding-calls?limit=5" -Method Get
    Write-Host "   ✅ Success!" -ForegroundColor Green
    Write-Host "   Total Embedding Calls Stored: $($embeddings.total)" -ForegroundColor White
    Write-Host "   Recent Calls Returned: $($embeddings.embedding_calls.Count)" -ForegroundColor White
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Export
Write-Host "4. Testing /observability/ai-metrics/export" -ForegroundColor Yellow
try {
    $export = Invoke-RestMethod -Uri "http://localhost:8000/observability/ai-metrics/export?days=1" -Method Get
    Write-Host "   ✅ Success!" -ForegroundColor Green
    Write-Host "   Export contains summary and recent calls" -ForegroundColor White
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n=== Testing Complete ===" -ForegroundColor Cyan
Write-Host "`nNote: Metrics will populate as you process tickets with LLM calls." -ForegroundColor Yellow
Write-Host ""

