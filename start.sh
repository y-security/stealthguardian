#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if docker-compose is installed
if ! command_exists docker-compose; then
    echo "docker-compose is not installed. Please install it and try again."
    exit 1
else
    echo "Check passed: docker-compose is installed."
fi

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the .env file
ENV_FILE="$SCRIPT_DIR/.env"

# Path to the docker-compose.yml file
DOCKER_COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

# Path to the SSL directory
SSL_DIR="$SCRIPT_DIR/ssl"

# Check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo ".env file does not exist in the script directory."
    exit 1
else
    echo "Check passed: .env file exists."
fi

# Check if the .env file contains the default API key
if grep -q "APIKEY=YareyouusingthedefaultkeyY" "$ENV_FILE"; then
    echo "Error: Default API key is being used. Please change the API key in the .env file."
    exit 1
else
    echo "Check passed: Default API key is not used."
fi

# Check if the docker-compose.yml file exists
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "docker-compose.yml file does not exist in the script directory."
    exit 1
else
    echo "Check passed: docker-compose.yml file exists."
fi

# Check if SSL files exist
if [ ! -f "$SSL_DIR/certfile.pem" ] || [ ! -f "$SSL_DIR/keyfile.pem" ]; then
    echo "SSL certificate files (certfile.pem and keyfile.pem) do not exist in the ssl directory."
    read -p "Do you want to generate a new SSL certificate? (yes/no): " generate_ssl

    if [[ "$generate_ssl" == "yes" ]]; then
        read -p "Enter the Fully Qualified Domain Name (FQDN) for the SSL certificate: " fqdn

        # Generate new SSL certificates
        openssl req -newkey rsa:2048 -nodes -keyout "$SSL_DIR/keyfile.pem" -x509 -days 365 -out "$SSL_DIR/certfile.pem" -subj "/CN=$fqdn"

        echo "New SSL certificates generated."

        # Prompt to disable SSL verification in the .env file
        echo "SSL verification needs to be disabled in the .env file - or use a trusted certificate."

    else
        echo "SSL certificates are required. Exiting."
        exit 1
    fi
else
    echo "Check passed: SSL certificate files exist."
fi

# Function to get the value of a variable from the .env file
get_env_value() {
    local key="$1"
    local value=$(grep "^$key=" "$ENV_FILE" | cut -d'=' -f2)
    echo "$value"
}

# Function to resolve replicas value
resolve_replicas() {
    local replicas="$1"
    if [[ "$replicas" =~ ^\$\{(.+)\}$ ]]; then
        local replicas_var=${BASH_REMATCH[1]}
        replicas=$(get_env_value "$replicas_var")
    fi
    echo "$replicas"
}

# List all services, their images, and replicas in the docker-compose.yml file
echo "Services defined in the docker-compose.yml file:"

# Flag to indicate if we are within the services section
in_services_section=false

# Variables to store service information
service_name=""
image_name=""
replicas=1

# Specify the environment file
ENV_FILE=".env"

# Read the docker-compose.yml file line by line
while IFS= read -r line; do
    if [[ "$line" =~ ^services: ]]; then
        in_services_section=true
    elif [[ "$in_services_section" == true ]]; then
        # Check if the line is a new service definition
        if [[ "$line" =~ ^[[:space:]]{2}[^[:space:]]+ ]]; then
            # Print the previous service details if available
            if [[ -n "$service_name" && -n "$image_name" ]]; then
                resolved_replicas=$(resolve_replicas "$replicas")
                echo "Service: $service_name"
                echo "  Image: $image_name"
                echo "  Replicas: $resolved_replicas"

                # Check for stealthguardian-cs-integration service and replicas
                if [[ "$service_name" == "stealthguardian-cs-integration" && "$resolved_replicas" -eq 1 ]]; then
                    # Check the environment file for CobaltStrike_Directory
                    cs_directory=$(get_env_value "CobaltStrike_Directory")
                    if [[ -n "$cs_directory" ]]; then
                        if [ ! -d "$cs_directory" ]; then
                            echo "Error: CobaltStrike_Directory '$cs_directory' does not exist."
                            exit 1
                        else
                            echo "Check passed: CobaltStrike_Directory '$cs_directory' exists."
                        fi
                    else
                        echo "Error: CobaltStrike_Directory is not set in the .env file."
                        exit 1
                    fi

                    # Check if UseCobaltStrike is enabled
                    use_cs=$(get_env_value "UseCobaltStrike")
                    if [[ "$use_cs" == "1" ]]; then
                        echo "CobaltStrike is enabled."
                    else
                        echo "CobaltStrike is not enabled."
                    fi
                fi
            fi
            # Reset variables for the new service
            service_name=$(echo "$line" | sed 's/://g' | sed 's/^\s*//')
            image_name=""
            replicas=1

            # Check if the replicas are defined in the .env file
            env_replicas_key="${service_name^^}_REPLICAS"  # Convert service name to uppercase and append _REPLICAS
            env_replicas=$(get_env_value "$env_replicas_key")
            if [[ -n "$env_replicas" ]]; then
                replicas="$env_replicas"
            fi
        elif [[ "$line" =~ image: ]]; then
            image_name=$(echo "$line" | awk '{print $2}')
        elif [[ "$line" =~ replicas: ]]; then
            replicas=$(echo "$line" | awk '{print $2}')
        fi
    fi
done < "$DOCKER_COMPOSE_FILE"

# Print the last service details if available
if [[ -n "$service_name" && -n "$image_name" ]]; then
    resolved_replicas=$(resolve_replicas "$replicas")
    echo "Service: $service_name"
    echo "  Image: $image_name"
    echo "  Replicas: $resolved_replicas"

    # Check for stealthguardian-cs-integration service and replicas
    if [[ "$service_name" == "stealthguardian-cs-integration" && "$resolved_replicas" -eq 1 ]]; then
        # Check the environment file for CobaltStrike_Directory
        cs_directory=$(get_env_value "CobaltStrike_Directory")
        if [[ -n "$cs_directory" ]]; then
            if [ ! -d "$cs_directory" ]; then
                echo "Error: CobaltStrike_Directory '$cs_directory' does not exist."
                exit 1
            else
                echo "Check passed: CobaltStrike_Directory '$cs_directory' exists."
            fi
        else
            echo "Error: CobaltStrike_Directory is not set in the .env file."
            exit 1
        fi

        # Check if UseCobaltStrike is enabled
        use_cs=$(get_env_value "UseCobaltStrike")
        if [[ "$use_cs" == "1" ]]; then
            echo "CobaltStrike is enabled."
        else
            echo "CobaltStrike is not enabled."
        fi
    fi
fi

echo "All checks passed."

# Prompt the user to press Enter to continue
read -p "Press Enter to continue and start docker-compose up..."

# Run docker-compose up
docker-compose up
