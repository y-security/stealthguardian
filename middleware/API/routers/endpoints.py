from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import sqlite3
import uuid
from auth import get_api_key, get_endpoint_agent_key

router = APIRouter()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn

############################################################################
# Return all available endpoints (agents) to the user
############################################################################

# Define a Pydantic model for the response
class Endpoint(BaseModel):
    id: int
    uuid: str
    name: str
    activated: int
    agentmodules: int
    referenceBeacon: str

# Define the GET endpoint to fetch all data from the 'endpoints' table
@router.get("/endpoints", response_model=List[Endpoint], summary="Return Endpoints", description="Returns all Endpoints", tags=["Endpoint"])
async def read_endpoints(api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM endpoints")
    rows = cursor.fetchall()
    conn.close()
    # Convert rows to list of Endpoint models
    endpoints = [Endpoint(id=row['id'], uuid=row["uuid"], name=row['name'], activated=row['activated'],  agentmodules=row['agentmodules'],  referenceBeacon=row['referenceBeacon']) for row in rows]
    return endpoints

############################################################################
# Register a new endpoint (agent)
# Returns a UUID and SSL client certificate (?)
# do this in admin panel so we have no self registration
############################################################################

# Pydantic model for the response
class UUIDResponse(BaseModel):
    uuid: str

# Define the GET endpoint to generate and return a UUID
@router.get("/generate-uuid", response_model=UUIDResponse, summary="Returns a new UUID for Agent registration", description="Returns a UUID which will be the StealthGuardianEndpointAPIKey of an Agent", tags=["Endpoint"])
async def generate_uuid():
    # Generate a new UUID
    new_uuid = str(uuid.uuid4())
    
    # Save the UUID to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO endpoints (uuid) VALUES (?)", (new_uuid,))
    conn.commit()
    conn.close()

    # Return the generated UUID
    return {"uuid": new_uuid}

############################################################################
# Activate an endpoint (agent)
# Returns the configuration file for an agent
############################################################################
class ActivationRequest(BaseModel):
    uuid: str
    name: str

# Define the POST endpoint to activate an endpoint
@router.post("/activate", summary="Activates an Endpoint", description="Activates an endpoint with an StealthGuardianEndpointAPIKey", tags=["Endpoint"])
async def activate_endpoint(request: ActivationRequest, endpoint_api_key: str = Depends(get_endpoint_agent_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # check if the given uuid if the agent actually belongs to the API key
    if not endpoint_api_key == request.uuid:
        conn.close()
        raise HTTPException(status_code=404, detail="UUID does not match with API key")

    # Check if the endpoint exists and is currently deactivated
    cursor.execute("SELECT activated FROM endpoints WHERE uuid = ?", (request.uuid,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="UUID not found")

    if row["activated"] == 1:
        conn.close()
        raise HTTPException(status_code=400, detail="Endpoint is already activated")

    # select configuration of default scan profile
    cursor.execute("SELECT value FROM middlewareconfiguration WHERE key = ?", ("default_scan_profile",))
    row = cursor.fetchone()

    if row:
        value = int(row[0])
        
        # Step 2: Check if the value is an integer
        if isinstance(value, int):
            # Step 3: Check if the integer is a valid id in the modulegroups table
            cursor.execute("SELECT COUNT(*) FROM modulegroups WHERE id = ?", (value,))
            valid_id_count = cursor.fetchone()[0]
            
            if valid_id_count > 0:
                # Step 4: Save the valid id in a variable
                valid_id = value
                print(f"Valid ID found: {valid_id}")
                # Update the endpoint with the new details and set activated to 1
                cursor.execute("""
                    UPDATE endpoints
                    SET name = ?, activated = 1, agentmodules = ?
                    WHERE uuid = ? AND activated = 0
                """, (request.name, valid_id, request.uuid, ))
            else:
                print("The integer is not a valid id in the modulegroups table.")
        else:
            print("The value is not an integer.")
    else:
        print("No value returned from the query.")

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Endpoint activated successfully"}


############################################################################
# Returne configuration for an endpoint (agent)
# Returns the configuration file for an agent
############################################################################
# Pydantic model for the POST request body for configuration retrieval
class ConfigurationRequest(BaseModel):
    uuid: str 

class ScanModule(BaseModel):
    id: int
    name: str
    script: str

# Pydantic model for the configuration response
class ConfigurationResponse(BaseModel):
    system: str
    endpoint: str
    port: int
    modules: List[ScanModule]
    uuid: str


# Define the POST endpoint to get configuration
@router.post("/get-configuration", response_model=ConfigurationResponse, summary="Get Configuration for an Endpoint", description="Returns the configuration for a specific endpoint", tags=["Endpoint"])
async def get_configuration(request: ConfigurationRequest, endpoint_api_key: str = Depends(get_endpoint_agent_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # check if the given uuid if the agent actually belongs to the API key
    if not endpoint_api_key == request.uuid:
        conn.close()
        raise HTTPException(status_code=404, detail="UUID does not match with API key")

    # Retrieve the configuration from the database
    cursor.execute("SELECT name, agentmodules FROM endpoints,middlewareconfiguration WHERE uuid = ?", (request.uuid,))
    endpoint_row = cursor.fetchone()
    
    if endpoint_row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="UUID not found")

    # Retrieve the host and port from middlewareconfiguration table
    cursor.execute("SELECT value FROM middlewareconfiguration WHERE key = ?", ("endpoint",))
    endpoint_config_row = cursor.fetchone()
    
    cursor.execute("SELECT value FROM middlewareconfiguration WHERE key = ?", ("port",))
    port_config_row = cursor.fetchone()
    
    if endpoint_config_row is None or port_config_row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Middleware configuration not found")

    # Retrieve the required modules from the database
    cursor.execute("SELECT mapped_module FROM modulegroupentries WHERE mapped_modulegroup = ?", (endpoint_row["agentmodules"],))
    agent_modules = cursor.fetchall()
    return_modules = []

    for module in agent_modules:
        cursor.execute("SELECT id, name, script FROM modules WHERE id = ?", (str(module["mapped_module"]),))
        temp_module = cursor.fetchone()
        return_modules.append( {"id": temp_module["id"], "name": temp_module["name"], "script": temp_module["script"]})

    # Prepare the configuration response
    configuration = ConfigurationResponse(
        system=endpoint_row["name"],
        endpoint=endpoint_config_row["value"],
        port=port_config_row["value"],
        modules=return_modules,
        uuid=request.uuid
    )
    
    # Close the connection
    conn.close()
    
    return configuration


############################################################################
# Assign Beacon to agent
############################################################################
class SetReferenceBeaconRequest(BaseModel):
    agentUUID: str
    beaconUUID: str

# Define the POST endpoint to update an entry in the modules table
@router.post("/endpoints/assign", summary="Assign Beacon to Agent", description="Mapping between a Beacon and Agent for Log correlation", tags=["Endpoint"])
async def update_endpoint_reference(request: SetReferenceBeaconRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM beacons WHERE uuid = ?", (request.beaconUUID,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"message": "Reference beacon does not exist!"}

    # Update the specified entry in the middlewareconfiguration table
    cursor.execute("UPDATE endpoints SET referenceBeacon = ? WHERE uuid = ?", (request.beaconUUID, request.agentUUID))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Endpoint entry not found!")
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Reference Beacon updated successfully"}


############################################################################
# Assign Scanprofile to Agent
############################################################################
class SetScanProfileAgentRequest(BaseModel):
    agentUUID: str
    scanProfileId: int

# Define the POST endpoint to update an entry in the modules table
@router.post("/endpoints/assignscanprofile", summary="Assign Scan Profile to Agent", description="Assign a Scan Profile to an Agent", tags=["Endpoint"])
async def update_scan_profile(request: SetScanProfileAgentRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM modulegroups WHERE id = ?", (request.scanProfileId,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"message": "Scan Profile does not exist!"}

    # Update the specified entry in the middlewareconfiguration table
    cursor.execute("UPDATE endpoints SET agentmodules = ? WHERE uuid = ?", (request.scanProfileId, request.agentUUID))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Agent entry not found!")
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Scan Profile updated successfully"}