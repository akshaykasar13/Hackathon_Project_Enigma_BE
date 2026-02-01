# Quick script to check if backend is running on port 8000

Write-Host "Checking if backend is running on port 8000..." -ForegroundColor Cyan

# Method 1: Check netstat
$netstat = netstat -ano | findstr :8000
if ($netstat) {
    Write-Host "`n[FOUND] Backend IS running on port 8000" -ForegroundColor Red
    Write-Host "Details:" -ForegroundColor Yellow
    $netstat | ForEach-Object { Write-Host "  $_" }
    
    # Extract PID
    $processId = ($netstat -split '\s+')[-1]
    if ($processId) {
        Write-Host "`nProcess ID: $processId" -ForegroundColor Yellow
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Process: $($process.ProcessName)" -ForegroundColor Yellow
            Write-Host "Path: $($process.Path)" -ForegroundColor Yellow
        }
        
        Write-Host "`nTo stop the backend, run:" -ForegroundColor Cyan
        Write-Host "  Stop-Process -Id $processId -Force" -ForegroundColor White
        Write-Host "  OR" -ForegroundColor Cyan
        Write-Host "  taskkill /PID $processId /F" -ForegroundColor White
    }
} else {
    Write-Host "`n[NOT FOUND] Backend is NOT running on port 8000" -ForegroundColor Green
}

# Method 2: Test connection
Write-Host "`nTesting connection..." -ForegroundColor Cyan
try {
    $test = Test-NetConnection -ComputerName localhost -Port 8000 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($test.TcpTestSucceeded) {
        Write-Host "[CONFIRMED] Port 8000 is accessible" -ForegroundColor Red
    } else {
        Write-Host "[CONFIRMED] Port 8000 is NOT accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "[CONFIRMED] Port 8000 is NOT accessible" -ForegroundColor Green
}

Write-Host "`n" -NoNewline

