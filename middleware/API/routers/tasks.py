from fastapi import APIRouter, HTTPException, Depends , APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import sqlite3
import uuid
import time
from typing import Optional, Literal
from auth import get_api_key
import base64

router = APIRouter()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn

############################################################################
# List beacon tasks
############################################################################
# Pydantic model for the configuration entry
class TaskEntry(BaseModel):
    id: int
    taskid: str
    timestamp: str
    source: str
    sourceBeacon: str
    targetBeacon: str
    command: str
    status: str
    result: str
    additionalcomandinfos: bytes

# Define the GET endpoint to return all entries from the beacon_tasks table
@router.get("/tasks", response_model=list[TaskEntry], summary="Return all Beacon Tasks", description="Returns all Beacon Tasks", tags=["Beacon"])
async def get_all_tasks(api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all entries from the beacon_tasks table
    cursor.execute("SELECT * FROM beacon_tasks")
    rows = cursor.fetchall()
    conn.close()

    # Convert the rows to a list of TaskEntry models
    configurations = [TaskEntry(id=row["id"], taskid=row["taskid"], timestamp=row["timestamp"], source=row["source"], sourceBeacon=row["sourceBeacon"], targetBeacon=row["targetBeacon"], command=row["command"], status=row["status"], result=row["result"], additionalcomandinfos=row["additionalcomandinfos"]) for row in rows]
    
    return configurations


############################################################################
# Seperate Endpoint for uploading files
############################################################################
@router.post("/tasks/add/withfile", summary="Upload a file with a reference", description="Endpoint to upload a file and a filereference using multipart form data", tags=["Beacon"])
async def upload_file(
    source: str = Form(...),
    sourceBeacon: str = Form(...),
    targetBeacon: str = Form(...),
    command: str = Form(...),
    additionalcomandinfos: UploadFile = File(...),
):
    file_content = await additionalcomandinfos.read()

    #content_str = file_content.decode('utf-8')[:-1]
    content_bytes = base64.b64encode(file_content)

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the beacon exists
    cursor.execute("SELECT * FROM beacons WHERE buid = ?", (targetBeacon,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Target beacon not found")

    # Check if the beacon exists
    cursor.execute("SELECT * FROM beacons WHERE buid = ?", (sourceBeacon,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Source beacon not found")

    # generate new task uuid
    new_uuid = str(uuid.uuid4())
    timestamp = int(time.time())
    status = "queued"

    # Insert the new key and value into the beacon_tasks table

    cursor.execute("INSERT INTO beacon_tasks (taskid, timestamp, source, sourceBeacon, targetBeacon, command, additionalcomandinfos, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (new_uuid, timestamp, source, sourceBeacon, targetBeacon, command, content_bytes, status))
    # Commit the transaction and close the connection

    conn.commit()
    conn.close()


    # Process the uploaded file and filereference as needed
    return {
        "source": source,
        "sourceBeacon": sourceBeacon,
        "targetBeacon": targetBeacon,
        "command": command,
    }


############################################################################
# Update and add new Tasks
############################################################################

class NewTaskRequest(BaseModel):
    source: str
    sourceBeacon: str
    targetBeacon: str
    command: str
#    additionalcomandinfos: Optional[str] = None  # this may be a reference to a file

@router.post("/tasks/add", summary="Add a new Beacon Task", description="Adds a new Tasks to a Beacon which will be executed against the reference", tags=["Beacon"])
async def new_script(request: NewTaskRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the beacon exists
    cursor.execute("SELECT * FROM beacons WHERE buid = ?", (request.targetBeacon,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Target beacon not found")

    # Check if the beacon exists
    cursor.execute("SELECT * FROM beacons WHERE buid = ?", (request.sourceBeacon,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Source beacon not found")

    # generate new task uuid
    new_uuid = str(uuid.uuid4())
    timestamp = int(time.time())
    status = "queued"

    # Insert the new key and value into the beacon_tasks table
    cursor.execute("INSERT INTO beacon_tasks (taskid, timestamp, source, sourceBeacon, targetBeacon, command, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (new_uuid, timestamp, request.source, request.sourceBeacon, request.targetBeacon, request.command, status))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Task added successfully!"}


############################################################################
# Filter for  tasks, having the source set to X
############################################################################

# New endpoint to filter tasks by status 'queued' and a user-supplied source
@router.get("/tasks/{source}", response_model=List[TaskEntry], summary="Return all Tasks filtered by a source", description="Returns all Tasks filtered by a source, which is the adversary tool",tags=["Beacon"])
async def get_tasks_by_source_and_status(source: str, api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beacon_tasks WHERE status = 'queued' AND source = ?", (source,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No tasks found for the given source with status 'queued'")
    configurations = [TaskEntry(id=row["id"], taskid=row["taskid"], timestamp=row["timestamp"], source=row["source"], sourceBeacon=row["sourceBeacon"], targetBeacon=row["targetBeacon"], command=row["command"], status=row["status"], result=row["result"], additionalcomandinfos=row["additionalcomandinfos"]) for row in rows]
    return configurations


############################################################################
# Filter for  tasks, having the sourceBeacon set to X
############################################################################

# New endpoint to filter tasks by status 'queued' and a user-supplied source
@router.get("/tasks/filter/{sourceBeacon}", response_model=List[TaskEntry], summary="Return all Tasks filtered by sourceBeacon", description="Returns all Tasks filtered by a sourceBeacon", tags=["Beacon"])
async def get_tasks_by_sourceBeacon(sourceBeacon: str, api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beacon_tasks WHERE targetBeacon = ?", (str(sourceBeacon),))
    rows = cursor.fetchall()
    conn.close() 
    if not rows:
        raise HTTPException(status_code=200, detail="No tasks found for the given Beacon")
    configurations = [TaskEntry(id=row["id"], taskid=row["taskid"], timestamp=row["timestamp"], source=row["source"], sourceBeacon=row["sourceBeacon"], targetBeacon=row["targetBeacon"], command=row["command"], status=row["status"], result=row["result"], additionalcomandinfos=row["additionalcomandinfos"]) for row in rows]
    return configurations



############################################################################
# Update Task with new status
############################################################################

class UpdateTaskRequest(BaseModel):
    taskid: str
    status: Literal['queued', 'executed', 'completed', 'notified']
    result: Optional[str] = None

# Define the POST endpoint to update an entry in the middlewareconfiguration table
@router.post("/tasks/update", summary="Updates status of a Task", description="Updates status of a Task after it was processed", tags=["Beacon"])
async def update_task_Status(request: UpdateTaskRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the specified entry in the middlewareconfiguration table
    if(request.result and request.status == "completed"):
        cursor.execute("UPDATE beacon_tasks SET status = ?, result = ? WHERE taskid = ?", (request.status, request.result, request.taskid))
    elif(request.result and request.status == "executed"):
        cursor.execute("UPDATE beacon_tasks SET status = ?, result = ? WHERE taskid = ?", (request.status, request.result, request.taskid))
    else:
        cursor.execute("UPDATE beacon_tasks SET status = ? WHERE taskid = ?", (request.status, request.taskid))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="ID not found")
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Task updated successfully"}
