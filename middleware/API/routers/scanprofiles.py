from fastapi import APIRouter, Depends, HTTPException
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

############################################################################
# Return configuration of agent scan profiles
############################################################################
# Pydantic models for the response
class Module(BaseModel):
    id: int
    name: str
    script: str

# Pydantic models for the response
class ModuleGroupEntry(BaseModel):
    id: int
    module_name: str

class ModuleGroup(BaseModel):
    id: int
    name: str
    entries: List[ModuleGroupEntry]


# Define the GET endpoint to return data from the modulegroups table along with their modulegroupentries
@router.get("/scanmodules", response_model=List[ModuleGroup], summary="Return Scan Modules", description="Returns all configured Scan Modules", tags=["Script"])
async def get_scanmodules(api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all module groups
    cursor.execute("SELECT * FROM modulegroups")
    modulegroups = cursor.fetchall()

    # Retrieve all module group entries and join with modules to get module names
    cursor.execute("""
        SELECT modulegroupentries.id, modulegroupentries.mapped_modulegroup, modules.name as module_name
        FROM modulegroupentries
        JOIN modules ON modulegroupentries.mapped_module = modules.id
    """)
    modulegroupentries = cursor.fetchall()
    conn.close()

    # Create a dictionary to map module group entries to their respective module groups
    group_entries_map = {}
    for entry in modulegroupentries:
        entry_model = ModuleGroupEntry(
            id=entry["id"],
            module_name=entry["module_name"]
        )
        if entry["mapped_modulegroup"] not in group_entries_map:
            group_entries_map[entry["mapped_modulegroup"]] = []
        group_entries_map[entry["mapped_modulegroup"]].append(entry_model)

    # Convert the rows to a list of ModuleGroup models
    module_groups = []
    for group in modulegroups:
        group_id = group["id"]
        entries = group_entries_map.get(group_id, [])
        module_groups.append(ModuleGroup(id=group_id, name=group["name"], entries=entries))
    
    return module_groups


############################################################################
# Update and add Scan Profiles
############################################################################

class UpdateScanProfileRequest(BaseModel):
    module_id: int
    profile_id: int

# Define the POST endpoint to update an entry in the modules table
@router.post("/scanmodules/update", summary="Update a Scan Module", description="Can be used to add Scripts to a Scan Module", tags=["Script"])
async def update_scanprofile(request: UpdateScanProfileRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the key already exists
    cursor.execute("SELECT * FROM modulegroupentries WHERE mapped_module = ? and mapped_modulegroup = ?", (request.module_id,request.profile_id,))
    row = cursor.fetchone()

    if row:
        conn.close()
        raise HTTPException(status_code=400, detail="Entry already exists")

    # Update the specified entry in the middlewareconfiguration table
    cursor.execute("INSERT INTO modulegroupentries (mapped_module, mapped_modulegroup) VALUES (?, ?)", (request.module_id, request.profile_id))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Configuration updated successfully"}

class NewScanProfileEntry(BaseModel):
    module_id: int

class NewScanProfileRequest(BaseModel):
    name: str
    entries: List[NewScanProfileEntry]

@router.post("/scanmodules/add", summary="Add a Scan Module", description="Can be used to add a Scan Module", tags=["Script"])
async def add_scan_profile(request: NewScanProfileRequest, api_key: str = Depends(get_api_key)):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the new profile into the modulegroups table
    cursor.execute("INSERT INTO modulegroups (name) VALUES (?)", (request.name,))
    modulegroup_id = cursor.lastrowid

    # Insert each entry into the modulegroupentries table
    for entry in request.entries:
        cursor.execute("INSERT INTO modulegroupentries (mapped_module, mapped_modulegroup) VALUES (?, ?)", (entry.module_id, modulegroup_id))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    
    return {"message": "Scan profile added successfully"}


