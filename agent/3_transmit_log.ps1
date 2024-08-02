param(
    [string]$Mode = "auto"
)

# Check if the parameter Mode is provided
if ($MyInvocation.BoundParameters.ContainsKey('Mode')) {
    if ($Mode -ne "manual") {
        $Mode = "auto"
    }
}

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
$url = "$baseUrl/api/agentlogs/add"


$disablessl=1

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


function Generate-RandomString {
    param (
        [int]$length = 12
    )

    $bytes = New-Object byte[] $length
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)

    $chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    $string = -join ($bytes | ForEach-Object { $chars[$_ % $chars.Length] })

    return $string
}

# loop over the modules and for each check the log and transmit it
foreach ($module in $jsonObject.modules) {
    # Step 3: Print the 'name' key for each entry in the array
    Write-Output $module.name
    $script_result = Invoke-Expression $module.script
    $status = if ($script_result.Length -gt 5) { "detected" } else { "undetected" }

    # Define the JSON payload
    $jsonPayload = @{
        agentuuid = $uuid
        status = $status
        raw_event =  "$script_result"
        check_type = $Mode
        module_uuid = Generate-RandomString -length 12
        executed_module = $module.id
    } | ConvertTo-Json

    try {
        # Make the POST request
        $response = Invoke-WebRequest -Uri $url -Method Post -Body $jsonPayload -ContentType "application/json" -ErrorAction Stop -Headers @{"StealthGuardianEndpointAPIKey" = $uuid}
    
        # Check if the response status code is 200
        if ($response.StatusCode -eq 200) {
            # Parse the response content
            $responseContent = $response.Content | ConvertFrom-Json
        
            # Check if the response message is "Log Entry added successfully!"
            if ($responseContent.message -eq "Log Entry added successfully!") {
                Write-Output "Log entry added successfully!"
            } elseif ($responseContent.message -eq "Log Entry already exists!"){
                Write-Output "Log Entry already exists!"
            } else {
                Write-Error "Unexpected response message: $($responseContent.message)"
            }
        } else {
            Write-Error "Unexpected status code: $($response.StatusCode)"
        }
    } catch {
        Write-Error "An error occurred: $_"
    }
}