# ScriptName: Defender Threat Check
# Define a function to get Windows Defender alerts
function Get-WindowsDefenderAlerts {
    # Get the latest threats detected by Windows Defender
    $threats = Get-MpThreatDetection

    # Sort threats by detection time in descending order
    $latestThreats = $threats | Sort-Object -Property InitialDetectionTime -Descending

    # Return the latest threats
    return $latestThreats
}

function Get-LatestDetectionContent {
    # Define the path to the file
    $filePath = Join-Path -Path (Get-Location) -ChildPath "latest_detection"

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

# Call the function and store the result in a variable
$threats = Get-WindowsDefenderAlerts

# Create an array to hold the filtered threat information
$filteredThreats = @()

$lastcheck = Get-LatestDetectionContent
# Loop over the entries and select specific properties
foreach ($threat in $threats) {

    if($lastcheck -eq "$($threat.DetectionID)") {
        break
    } 

    $exists = $filteredThreats | Where-Object { $_.ThreatId -eq "$($threat.ThreatName)" }
    $threatDetails = Get-MpThreat | Where-Object { $_.ThreatID -eq "$($threat.ThreatId)" }

    if ($exists -eq $null) {
        $filteredThreat = [PSCustomObject]@{
            ThreatName  = $threatDetails.ThreatName
            ThreatId    = $threatDetails.ThreatId
            DetectionId  = $threat.DetectionId
        
        }
        # Add the filtered threat object to the array
        $filteredThreats += $filteredThreat
    }
}


# Convert the array of filtered threats to JSON
$filteredThreatsJson = $filteredThreats | ConvertTo-Json -Depth 3

# Print the JSON string of the first element
if ($filteredThreats.Count -gt 0) {
    $firstElementJson = $filteredThreats[0] 

    # Write the ThreatId of the first element into a file
    $firstElementThreatId = "$($firstElementJson.DetectionId)" -replace "\r\n|\n|\r", ""
    $firstElementThreatId | Out-File -FilePath "latest_detection" -NoNewline
} 

Write-Output $filteredThreatsJson
