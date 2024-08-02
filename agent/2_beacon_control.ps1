# Define the path to the JSON file
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$jsonFilePath = "$scriptDirectory\configuration.json"

# Check if the file exists
if (Test-Path $jsonFilePath) {
    # Read the content of the JSON file
    $jsonContent = Get-Content -Path $jsonFilePath -Raw

    # Convert the JSON content to a PowerShell object
    $jsonObject = $jsonContent | ConvertFrom-Json
} else {
    Write-Output "The file does not exist: $jsonFilePath"
    exit 1
}

# Add Sanity checks here to verify if expected keys exists
$requiredKeys = @("system", "endpoint", "port", "uuid", "modules")
$missingKeys = @()
foreach ($key in $requiredKeys) {
    if (-not $jsonObject.PSObject.Properties.Name.Contains($key)) {
        $missingKeys += $key
    }
}

if ($missingKeys.Count -gt 0) {
    Write-Output "The following required keys are missing: $($missingKeys -join ', ')"
    exit 1
}

# Extract values from the configuration
$system = $jsonObject.system
$endpoint = $jsonObject.endpoint
$port = $jsonObject.port
$uuid =  $jsonObject.uuid

$baseUrl = "https://${endpoint}:$port"

# Construct the URL using the endpoint and port
$url = "$baseUrl/api/agenttask/$uuid"


$disablessl=0

# Define a function to set the trust all certificates policy
function Set-TrustAllCertificates {
    # Check if the type TrustAllCertsPolicy already exists
    if (-not ([type]::GetType('TrustAllCertsPolicy', $false, $false))) {
        try {
            Add-Type @"
            using System.Net;
            using System.Security.Cryptography.X509Certificates;
            public class TrustAllCertsPolicy : ICertificatePolicy {
                public bool CheckValidationResult(
                    ServicePoint srvPoint, X509Certificate certificate,
                    WebRequest request, int certificateProblem) {
                    return true;
                }
            }
"@ -ErrorAction Stop
        } catch {
            Write-Host "Type 'TrustAllCertsPolicy' already exists or another error occurred, continuing execution."
        }
    }
    [System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
}

# Check if $disablessl is set to 1 and set the trust all certificates policy if true
if ($disablessl -eq 1) {
    Set-TrustAllCertificates
}

try {
    # Assuming that the API response returns a JSON array of tasks
    $response = Invoke-RestMethod -Uri $url -Method Get  -Headers @{"StealthGuardianEndpointAPIKey" = $uuid}

    # Loop over the returned JSON entries
    foreach ($entry in $response) {
        # Ensure the command key exists in the entry
        if ($entry.PSObject.Properties.Name.Contains("command")) {
            $command = $entry.command
            $id = $entry.id

            # Handle different commands using a switch statement
            switch ($command) {
                "logcheck" {
                    # Call the foobar.ps1 script if the command is logcheck
                    Write-Output "foo"
                    & $scriptDirectory\3_transmit_log.ps1 -Mode "manual"
                }
                "updateconfig" {

                    # Prepare the data for the POST request to /api/get-configuration
                    $configData = @{
                        uuid = $uuid
                    } | ConvertTo-Json
                    
                    $configResponse = Invoke-WebRequest -Uri "$baseUrl/api/get-configuration" -Method Post -Body $configData -ContentType "application/json" -Headers @{"StealthGuardianEndpointAPIKey" = $uuid} -ErrorAction Stop -UseBasicParsing

                    if ($configResponse.StatusCode -eq 200) {
                        # Save the response to configuration.json
                        
                        $configResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonFilePath
                    } else {
                        Write-Error "Failed to get configuration. HTTP Status: $($configResponse.StatusCode)"
                    }
                }
                default {
                    Write-Output "Unknown command: $command"
                }
            }

            # Update the task status
            $updateUrl = "$baseUrl/api/agenttask/update"
            $postParams = @{
                id       = $id
                executed = 1
            }

            try {
                Invoke-RestMethod -Uri $updateUrl -Method Post -Body ($postParams | ConvertTo-Json) -ContentType "application/json"  -Headers @{"StealthGuardianEndpointAPIKey" = $uuid}
                Write-Output "Task with ID $id has been marked as executed."
            } catch {
                Write-Output "Failed to update task with ID $id. Status code: $($_.Exception.Response.StatusCode.Value__)."
            }
        } else {
            Write-Output "The command key is missing in one of the entries."
        }
    }
} catch {
    exit 1
}
