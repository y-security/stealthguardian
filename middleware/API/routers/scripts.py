from fastapi import APIRouter, HTTPException, Depends 
from pydantic import BaseModel
from typing import List
import sqlite3

from auth import get_api_key

router = APIRouter()

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models for the response
class Module(BaseModel):
    id: int
    name: str
    script: str

# Define the GET endpoint to return data from the modules table
@router.get("/scripts", response_model=List[Module], summary="Return all Scan Scripts", description="Returns all available Scan Scripts", tags=["Script"])
async def get_scripts(api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all entries from the modules table
    cursor.execute("SELECT * FROM modules")
    rows = cursor.fetchall()
    conn.close()

    # Convert the rows to a list of Module models
    modules = [Module(id=row["id"], name=row["name"], script=row["script"]) for row in rows]
    
    return modules

############################################################################
# Update and add Scripts
############################################################################

class UpdateScriptRequest(BaseModel):
    id: int
    name: str
    script: str

# Define the POST endpoint to update an entry in the modules table
@router.post("/scripts/update", summary="Update a Scan Script", description="Can be used to update an existing Scan Script", tags=["Script"])
async def update_script(request: UpdateScriptRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the specified entry in the middlewareconfiguration table
    cursor.execute("UPDATE modules SET script = ? WHERE id = ?", (request.script, request.id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="ID not found")
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Configuration updated successfully"}



class NewScriptRequest(BaseModel):
    name: str
    script: str

@router.post("/script/add", summary="Add a Scan Script", description="Can be used to add a Scan Script", tags=["Script"])
async def new_script(request: NewScriptRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM modules WHERE name = ?", (request.name,))
    row = cursor.fetchone()

    if row:
        conn.close()
        raise HTTPException(status_code=400, detail="Key already exists")

    # Insert the new key and value into the middlewareconfiguration table
    cursor.execute("INSERT INTO modules (name, script) VALUES (?, ?)", (request.name, request.script))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Script added successfully"}

