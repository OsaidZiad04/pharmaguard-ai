$ErrorActionPreference = "Continue"

function Write-Status($Message) {
    Write-Host "[PharmaGuard AI] $Message"
}

$Ports = @(3000, 8000)
$Stopped = @()

foreach ($Port in $Ports) {
    $Connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (!$Connections) {
        Write-Status "No listening process found on port $Port."
        continue
    }

    $ProcessIds = $Connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($ProcessId in $ProcessIds) {
        try {
            $Process = Get-Process -Id $ProcessId -ErrorAction Stop
            Write-Status "Stopping $($Process.ProcessName) (PID $ProcessId) on port $Port."
            Stop-Process -Id $ProcessId -Force -ErrorAction Stop
            $Stopped += "$Port/$ProcessId"
        } catch {
            Write-Status "Warning: could not stop PID $ProcessId on port $Port. $($_.Exception.Message)"
        }
    }
}

if ($Stopped.Count -eq 0) {
    Write-Status "No PharmaGuard demo processes were stopped. If terminals are still open, close them manually."
} else {
    Write-Status "Stopped demo listeners: $($Stopped -join ', ')"
}
