from fastapi import HTTPException, status, Header
from fastapi.security import APIKeyHeader
from fastapi import Cookie

from typing import Optional
import sqlite3

import os
import uuid

API_KEY = os.environ.get('APIKEY', str(uuid.uuid4())) # this basically prevents anyone not setting an APIKEY
API_KEY_NAME = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
cookie_key = Cookie(name="access_token", auto_error=False)

# This is used to authenticate for the middleware
def get_api_key(
    StealthGuardianAPIKey: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None)
):
    if access_token == API_KEY:
        return access_token
    
    elif StealthGuardianAPIKey and StealthGuardianAPIKey == API_KEY:
        return StealthGuardianAPIKey
   
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key

# This is used to authenticate endpoint agents
# The UUID of an agent is used for authentication
# Database connection function
def get_db_connection():
    conn = sqlite3.connect('../database/middleware.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_endpoint_agent_key(
    StealthGuardianEndpointAPIKey: Optional[str] = Header(None),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    if StealthGuardianEndpointAPIKey:
        # Check if the endpoint exists and is currently deactivated
        cursor.execute("SELECT activated FROM endpoints WHERE uuid = ?", (StealthGuardianEndpointAPIKey,))
        row = cursor.fetchone()
        
        if row:
            return StealthGuardianEndpointAPIKey
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )  
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No API key given",
        )
    return api_key
