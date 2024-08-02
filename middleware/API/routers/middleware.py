from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import sqlite3
import json
from auth import get_api_key

router = APIRouter()

f = open('/API/config.json')
config = json.load(f)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint /
@router.get("/version", summary="Display version Information", description="Returns the tool's version", tags=["Middleware"])
def read_root():
    return {"TOOL": config['CONFIG']['SERVICE'], "Version": config['CONFIG']['Version'], }


############################################################################
# Return configuration of middleware
############################################################################
# Pydantic model for the configuration entry
class ConfigurationEntry(BaseModel):
    id: int
    key: str
    value: str

# Define the GET endpoint to return all entries from the middlewareconfiguration table
@router.get("/middlewareconfiguration", summary="Return Middleware Configuration", description="Returns all configuration settings of the Middleware", response_model=list[ConfigurationEntry], tags=["Middleware"])
async def get_all_configurations(api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all entries from the middlewareconfiguration table
    cursor.execute("SELECT * FROM middlewareconfiguration")
    rows = cursor.fetchall()
    conn.close()

    # Convert the rows to a list of ConfigurationEntry models
    configurations = [ConfigurationEntry(id=row["id"], key=row["key"], value=row["value"]) for row in rows]
    
    return configurations

############################################################################
# Update and add Middleware/Environment Settings
############################################################################

class UpdateConfigurationRequest(BaseModel):
    id: int
    value: str

# Define the POST endpoint to update an entry in the middlewareconfiguration table
@router.post("/middlewareconfiguration/update", summary="Update Middleware/Environment Settings", description="Updates a Setting in the Middleware/Environment Configuration", tags=["Middleware"])
async def update_middleware_configuration(request: UpdateConfigurationRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the specified entry in the middlewareconfiguration table
    cursor.execute("UPDATE middlewareconfiguration SET value = ? WHERE id = ?", (request.value, request.id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="ID not found")
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Configuration updated successfully"}



class NewConfigurationRequest(BaseModel):
    key: str
    value: str

@router.post("/middlewareconfiguration/add", summary="Add Middleware/Environment Setting", description="Adds a new Setting to the Middleware Configuration", tags=["Middleware"])
async def new_middleware_configuration(request: NewConfigurationRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM middlewareconfiguration WHERE key = ?", (request.key,))
    row = cursor.fetchone()

    if row:
        conn.close()
        raise HTTPException(status_code=400, detail="Key already exists")

    # Insert the new key and value into the middlewareconfiguration table
    cursor.execute("INSERT INTO middlewareconfiguration (key, value) VALUES (?, ?)", (request.key, request.value))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Configuration added successfully"}


