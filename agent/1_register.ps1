param (
    [string]$address,
    [int]$port
)

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


# Check if the configuration.json file exists in the current directory
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$configFilePath = "$scriptDirectory\configuration.json"

if (Test-Path -Path $configFilePath) {
    Write-Warning "The configuration.json file already exists. Stopping the script."
    exit
}

# Function to display usage
function Show-Usage {
    Write-Output "Usage: .\script.ps1 -address <address> -port <port>"
    exit
}

if (-not $address -or -not $port) {
    Show-Usage
}

# Construct the URL for the API requests
$baseUrl = "https://${address}:$port"

# Make a GET request to /api/generate-uuid
$response = Invoke-WebRequest -Uri "$baseUrl/api/generate-uuid" -Method Get -ContentType "application/json" -ErrorAction Stop

if ($response.StatusCode -eq 200) {
    $responseBody = $response.Content | ConvertFrom-Json
    $uuid = $responseBody.uuid
} else {
    Write-Error "Failed to get UUID. HTTP Status: $($response.StatusCode)"
    exit
}

# Get the hostname of the system
$hostname = $env:COMPUTERNAME

# Prepare the data for the POST request to /api/activate
$activateData = @{
    uuid = $uuid
    name = $hostname
} | ConvertTo-Json

# Make a POST request to /api/activate
try {
    $activateResponse = Invoke-WebRequest -Uri "$baseUrl/api/activate" -Method Post -Body $activateData -ContentType "application/json" -Headers @{"StealthGuardianEndpointAPIKey" = $uuid} -ErrorAction Stop
    $activateContent = $activateResponse.Content | ConvertFrom-Json
    
    if ($activateContent.message -eq "Endpoint activated successfully") {
        # Prepare the data for the POST request to /api/get-configuration
        $configData = @{
            uuid = $uuid
        } | ConvertTo-Json

        # Make a POST request to /api/get-configuration
        $configResponse = Invoke-WebRequest -Uri "$baseUrl/api/get-configuration" -Method Post -Body $configData -ContentType "application/json" -Headers @{"StealthGuardianEndpointAPIKey" = $uuid} -ErrorAction Stop
        
        if ($configResponse.StatusCode -eq 200) {
            # Save the response to configuration.json
            $configResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Out-File -FilePath $configFilePath
            Write-Output "Configuration saved to $configFilePath"
        } else {
            Write-Error "Failed to get configuration. HTTP Status: $($configResponse.StatusCode)"
        }
    } else {
        Write-Error "Activation failed. Response: $($activateContent.message)"
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Error "Error: The server responded with a 404 error."
    } else {
        Write-Error "An error occurred: $_"
    }
}