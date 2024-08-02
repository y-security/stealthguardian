from fastapi import APIRouter,  Depends
from pydantic import BaseModel
from typing import List
import sqlite3
import uuid
from auth import get_api_key
router = APIRouter()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn

############################################################################
# Return all available beacons to the user
############################################################################

# Define a Pydantic model for the response
class Beacon(BaseModel):
    id: int
    uuid: str
    buid: str
    name: str
    source: str
    status: str

# Define the GET endpoint to fetch all data from the 'beacons' table
@router.get("/beacons", response_model=List[Beacon], summary="Return all Beacons", description="Return all Beacons", tags=["Beacon"])
async def read_beacons(api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beacons")
    rows = cursor.fetchall()
    conn.close()
    # Convert rows to list of Beacon models
    beacons = [Beacon(id=row['id'], uuid=row["uuid"], buid=row["buid"], name=row['name'], source=row['source'], status=row['status']) for row in rows]
    return beacons




############################################################################
# Update and add new Beacon
############################################################################

class NewBeaconRequest(BaseModel):
    buid: str
    name: str
    source: str

@router.post("/beacons/add", summary="New Beacon", description="Register a new Beacon to the Middleware so that it can be assigned to an Endpoint/Agent", tags=["Beacon"])
async def new_agentlog(request: NewBeaconRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM beacons WHERE buid = ?", (request.buid,))
    row = cursor.fetchone()

    if row:
        conn.close()
        return {"message": "Beacon already exists!"}

    # generate new task uuid
    new_uuid = str(uuid.uuid4())
    status = "active"

    # Insert the new key and value into the middlewareconfiguration table
    cursor.execute("INSERT INTO beacons (uuid, buid, name, status, source) VALUES (?, ?, ?, ?, ?)", (new_uuid, request.buid, request.name, status, request.source))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Beacon added successfully!"}