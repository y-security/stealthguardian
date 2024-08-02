from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import sqlite3
import time
from auth import get_api_key, get_endpoint_agent_key

router = APIRouter()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn


############################################################################
# List agent taks
############################################################################
class AgentTaskEntry(BaseModel):
    id: int
    timestamp: str
    agentuuid: str
    command: str
    executed: int

# Define the GET endpoint to return all entries from the beacon_tasks table
@router.get("/agenttasks", response_model=list[AgentTaskEntry], summary="Return all Tasks of all Agents", description="Returns all Tasks of all Agents", tags=["Agent"])
async def get_all_agenttasks(api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all entries from the beacon_tasks table
    cursor.execute("SELECT * FROM agenttasks")
    rows = cursor.fetchall()
    conn.close()

    # Convert the rows to a list of AgentTaskEntry models
    configurations = [AgentTaskEntry(id=row["id"], agentuuid=row["agentuuid"], timestamp=row["timestamp"], command=row["command"], executed=row["executed"]) for row in rows]
    
    return configurations


###########################################################################
# Update and add new Task for Agent
############################################################################

class NewAgentTaskRequest(BaseModel):
    targetBeacon: str
    command: str

@router.post("/agenttask/add", summary="Add new Agent Task", description="Adds a new Tasks to the Agent which is then collected by the Agent", tags=["Agent"])
async def new_agenttask(request: NewAgentTaskRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM beacons WHERE buid = ?", (request.targetBeacon,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="No beacon found")

    cursor.execute("SELECT endpoints.uuid FROM endpoints JOIN beacons ON endpoints.referenceBeacon = beacons.uuid WHERE beacons.buid = ?", (request.targetBeacon,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise HTTPException(status_code=400, detail="No agent assigned to the beacon")

    # generate new task uuid
    timestamp = int(time.time())
    executed = 0

    # Insert the new key and value into the middlewareconfiguration table
    cursor.execute("INSERT INTO agenttasks (timestamp, agentuuid, command, executed) VALUES (?, ?, ?, ?)", (timestamp, result[0], request.command, executed))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Task Entry added successfully!"}


class AgentUpdateConfig(BaseModel):
    agentuuid: str

@router.post("/agenttask/updateconfig", summary="Let the agent update its content", description="Initiate config change to the Agent", tags=["Agent"])
async def new_agentconfig(request: AgentUpdateConfig, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM endpoints WHERE uuid = ?", (request.agentuuid,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="No agent found")

    # generate new task uuid
    timestamp = int(time.time())
    command = "updateconfig"
    executed = 0

    # Insert the new key and value into the middlewareconfiguration table
    cursor.execute("INSERT INTO agenttasks (timestamp, agentuuid, command, executed) VALUES (?, ?, ?, ?)", (timestamp, request.agentuuid, command, executed))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Config Change added successfully!"}


class UpdateAgentTaskRequest(BaseModel):
    id: int
    executed: int

# Define the POST endpoint to update an entry in the modules table
@router.post("/agenttask/update", summary="Change executed value", description="Can be used to change the executed column of a task entry to mark it as executed", tags=["Agent"])
async def update_agenttask(request: UpdateAgentTaskRequest, endpoint_api_key: str = Depends(get_endpoint_agent_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT agentuuid FROM agenttasks where id = ?", (request.id,))
    row = cursor.fetchone()

    # check if the given uuid if the agent actually belongs to the API key
    if not row :
        conn.close()
        raise HTTPException(status_code=404, detail="No Entries found")

    # check if the given uuid if the agent actually belongs to the API key

    if not row["agentuuid"] == endpoint_api_key:
        conn.close()
        raise HTTPException(status_code=404, detail="UUID does not match with API key")

    # Update the specified entry in the middlewareconfiguration table
    cursor.execute("UPDATE agenttasks SET executed = ? WHERE id = ?", (request.executed, request.id))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task entry not found!")
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Task entry updated successfully"}


############################################################################
# Filter for agenttasks, specific uuid
############################################################################
class AgentTaskRequestCommand(BaseModel):
    id: int
    command: str

@router.get("/agenttask/{agentid}", response_model=List[AgentTaskRequestCommand], summary="Filter Tasks for an Agent", description="Filter Agent Tasks for a specific Agent uuid", tags=["Agent"])
async def get_agenttask_by_agentuuid(agentid: str, endpoint_api_key: str = Depends(get_endpoint_agent_key)):

    # check if the given uuid if the agent actually belongs to the API key
    if not endpoint_api_key == agentid:
        raise HTTPException(status_code=404, detail="UUID does not match with API key")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,command FROM agenttasks WHERE agentuuid = ? and executed = 0", (agentid,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No outstanding tasks found")

    configurations = [AgentTaskRequestCommand(id=row["id"], command=row["command"]) for row in rows]
    return configurations
