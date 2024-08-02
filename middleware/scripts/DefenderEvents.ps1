# ScriptName: Defender Event Check
# Define a function to get Windows Defender notifications from the Event Log
function Get-WindowsDefenderNotifications {
    # Get the events from the Microsoft-Windows-Windows Defender/Operational log
    $events = Get-WinEvent -LogName "Microsoft-Windows-Windows Defender/Operational" | Where-Object {
        $_.Id -in 1001, 1002, 1007, 1010, 1116, 1117 # Common event IDs for Defender notifications
    }

    # Sort events by time created in descending order
    $latestEvents = $events | Sort-Object -Property TimeCreated -Descending

    # Output the latest events
    $latestEvents #| Select-Object TimeCreated, Id, RecordId, LevelDisplayName, Message | Format-Table -AutoSize

}

function Get-LatestDetectionContent {
    # Define the path to the file
    $filePath = Join-Path -Path (Get-Location) -ChildPath "latest_event"

    # Check if the file exists
    if (Test-Path -Path $filePath) {
        # Read the contents of the file into a variable
        $fileContent = Get-Content -Path $filePath -Raw
        return $fileContent
    }
    else {
        New-Item -Path $filePath -ItemType File -Force | Out-Null
        return $null
    }
}

function Check-DefenderScanMessage {
    param (
        [string]$inputString
    )

    # Define the patterns to check
    $patterns = @(
        "Microsoft Defender Antivirus scan has finished",
        "Microsoft Defender Antivirus scan has been stopped before completion"
    )

    # Check if the input string contains any of the patterns
    foreach ($pattern in $patterns) {
        if ($inputString -like "*$pattern*") {
            return $true
        }
    }

    return $false
}


# Call the function and store the result in a variable
$threats = Get-WindowsDefenderNotifications

# Create an array to hold the filtered threat information
$filteredThreats = @()

# Loop over the entries and select specific properties
foreach ($threat in $threats) {

    if(Get-LatestDetectionContent -eq $threat.RecordId) {
        break
    }

    $exists = $filteredThreats | Where-Object { $_.RecordId -eq $threat.RecordId }
    
    if ($exists -eq $null -and -not (Check-DefenderScanMessage -inputString $threat.Message)) {
        $filteredThreat = [PSCustomObject]@{
            LevelDisplayName  = $threat.LevelDisplayName
            RecordId    = $threat.RecordId
            Message  = $threat.Message
        
        }
        # Add the filtered threat object to the array
        $filteredThreats += $filteredThreat
    }
}

# Convert the array of filtered threats to JSON
$filteredThreatsJson = $filteredThreats | ConvertTo-Json -Depth 3

# Print the JSON string of the first element
if ($filteredThreats.Count -gt 0) {
    $firstElementJson = $filteredThreats[0] | ConvertTo-Json -Depth 3

    # Write the ThreatId of the first element into a file
    $firstElementThreatId = $filteredThreats[0].RecordId
    $firstElementThreatId | Out-File -FilePath "latest_event"
} 

Write-Output $filteredThreatsJson
