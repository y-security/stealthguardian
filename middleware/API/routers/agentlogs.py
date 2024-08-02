from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import sqlite3
import uuid
import time
from typing import Optional, Literal

from auth import get_api_key, get_endpoint_agent_key

router = APIRouter()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn

############################################################################
# List agent events
############################################################################
class AgentEventEntry(BaseModel):
    id: int
    logcheck: str
    agentuuid: str
    timestamp: str
    status: str
    raw_event: str
    check_type: str
    module_uuid: str
    executed_module: int
    notified: int

# Define the GET endpoint to return all entries from the beacon_tasks table
@router.get("/agentlogs", response_model=list[AgentEventEntry], summary="Return all Agent Logs", description="Returns all Logs send by Agents", tags=["Agent"])
async def get_all_agentlogs(api_key: str = Depends(get_api_key)):
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all entries from the beacon_tasks table
    cursor.execute("SELECT agent_logs.* FROM agent_logs")
    rows = cursor.fetchall()
    conn.close()

    # Convert the rows to a list of AgentEventEntry models
    configurations = [AgentEventEntry(id=row["id"], logcheck=row["logcheck"], agentuuid=row["agentuuid"], timestamp=row["timestamp"], status=row["status"], raw_event=row["raw_event"], check_type=row["check_type"], module_uuid=row["module_uuid"], executed_module=row["executed_module"], notified=row["notified"]) for row in rows]
    
    return configurations



############################################################################
# Get a specific Log from an Agent
############################################################################
@router.get("/agentlogs/log/{logcheck}", response_model=List[AgentEventEntry],  summary="Return a specific logs", description="Returns a specific log of an Agent, filtered by uuid of log entry", tags=["Agent"])
async def get_agentlog_by_id(logcheck: str, api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT agent_logs.* FROM agent_logs WHERE logcheck = ?", (logcheck,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No logs found for the given status")
    configurations = [AgentEventEntry(id=row["id"], logcheck=row["logcheck"], agentuuid=row["agentuuid"], timestamp=row["timestamp"], status=row["status"], raw_event=row["raw_event"], check_type=row["check_type"], module_uuid=row["module_uuid"], executed_module=row["executed_module"], notified=row["notified"]) for row in rows]
    return configurations


############################################################################
# Update and add new Log from Agent
############################################################################

class NewAgentLogRequest(BaseModel):
    agentuuid: str
    status: Literal['detected', 'undetected']
    raw_event: str
    check_type: str
    module_uuid: str
    executed_module: int

@router.post("/agentlogs/add", summary="Adds log for an Agent", description="Adds a new log entry for an Agent", tags=["Agent"])
async def new_agentlog(request: NewAgentLogRequest, endpoint_api_key: str = Depends(get_endpoint_agent_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    if not endpoint_api_key == request.agentuuid:
        conn.close()
        raise HTTPException(status_code=404, detail="UUID does not macht with API key")

    # Check if the key already exists
    cursor.execute("SELECT * FROM endpoints WHERE uuid = ?", (request.agentuuid,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="No agent found")

    # Check if we already have the submitted log in our database
    if(request.module_uuid != ''):
        cursor.execute("SELECT * FROM agent_logs WHERE module_uuid = ?", (request.module_uuid,))
        row = cursor.fetchone()

        if row:
            conn.close()
            return {"message": "Log Entry already exists!"}

    # generate new task uuid
    new_uuid = str(uuid.uuid4())
    timestamp = int(time.time())
    notified = 0

    # Insert the new key and value into the middlewareconfiguration table
    cursor.execute("INSERT INTO agent_logs (logcheck, agentuuid, timestamp, status, raw_event, check_type, module_uuid, executed_module, notified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (new_uuid, request.agentuuid, timestamp, request.status, request.raw_event, request.check_type, request.module_uuid, request.executed_module, notified))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Log Entry added successfully!"}


class UpdateLogRequest(BaseModel):
    logcheck: str
    notified: int

# Define the POST endpoint to update an entry in the modules table
@router.post("/agentlogs/update", summary="Change notified value", description="Can be used to change the notified column of a log entry to mark it after informing the user", tags=["Agent"])
async def update_agentlog(request: UpdateLogRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the specified entry in the middlewareconfiguration table
    cursor.execute("UPDATE agent_logs SET notified = ? WHERE logcheck = ?", (request.notified, request.logcheck))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Log entry not found!")
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Log entry updated successfully"}



############################################################################
# Filter for ageetlogs, having the notified set to X
############################################################################
class AgentEventEntryWithBuid(BaseModel):
    id: int
    logcheck: str
    agentuuid: str
    timestamp: str
    status: str
    raw_event: str
    check_type: str
    module_uuid: str
    executed_module: int
    notified: int
    buid: str

@router.get("/agentlogs/{notified}", summary="Filter for notified column of log entries", description="Returns all logs having notified set to a specific value", tags=["Agent"])
async def get_agentlog_by_status(notified: str, api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    #cursor.execute("SELECT agent_logs.*, beacons.buid FROM agent_logs JOIN endpoints ON agent_logs.agentuuid = endpoints.uuid JOIN beacons ON endpoints.referenceBeacon = beacons.uuid WHERE notified = ?", (notified,))
    cursor.execute("SELECT agent_logs.*, (SELECT DISTINCT beacon_tasks.sourceBeacon FROM beacon_tasks JOIN beacons ON beacons.buid = beacon_tasks.targetBeacon WHERE beacons.uuid = endpoints.referenceBeacon LIMIT 1) AS buid FROM agent_logs JOIN endpoints ON agent_logs.agentuuid = endpoints.uuid WHERE agent_logs.notified = ?;", (notified,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No logs found for the given status")

    configurations = [AgentEventEntryWithBuid(id=row["id"], logcheck=row["logcheck"], agentuuid=row["agentuuid"], timestamp=row["timestamp"], status=row["status"], raw_event=row["raw_event"], check_type=row["check_type"], module_uuid=row["module_uuid"], executed_module=row["executed_module"], notified=row["notified"], buid=row["buid"] if row["buid"] is not None else "") for row in rows]
    return configurations

############################################################################
# Filter for ageetlogs, belonging to a specific buid
############################################################################
class AgentEventSmall(BaseModel):
    timestamp: str
    status: str
    logcheck: str

@router.get("/agentlogs/filter/{sourceBeacon}", summary="Filter for specific beacon log entries", description="Returns all log entries of a specific beacon", tags=["Agent"])
async def get_agentlog_by_sourceBeacon(sourceBeacon: str, api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT agent_logs.*
    FROM agent_logs
    JOIN endpoints ON agent_logs.agentuuid = endpoints.uuid
    JOIN beacons ON endpoints.referenceBeacon = beacons.uuid
    WHERE beacons.buid = ?
    ''', (sourceBeacon,))

    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=200, detail="No logs found for the given status")
    configurations = [AgentEventSmall(timestamp=row["timestamp"], status=row["status"], logcheck=row["logcheck"]) for row in rows]
    return configurations

