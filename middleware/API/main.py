from fastapi import FastAPI, HTTPException, Depends, Request, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN
from auth import get_api_key
from starlette.middleware.base import BaseHTTPMiddleware
from jinja2 import TemplateNotFound
import os
import uuid
import uuid


from routers import (
    endpoints,
    middleware,
    scanprofiles,
    scripts,
    tasks,
    agentlogs,
    beacons,
    agenttasks,
)


class CustomStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope) -> Response:
        full_path, stat_result = self.lookup_path(path)
        if stat_result and os.path.isfile(full_path):
            # Modify the file content on the fly here
            with open(full_path, "rb") as file:
                content = file.read()
                modified_content = content
                # Example modification: convert content to uppercase
                disablesslverify = os.environ.get("DisableSSLVerification", "False")
                if disablesslverify.lower() == "true":
                    modified_content = content.replace(
                        b"$disablessl=0", b"$disablessl=1"
                    )
                return Response(modified_content, media_type="text/plain")
        return await super().get_response(path, scope)


tags_metadata = [
    {
        "name": "Endpoint",
        "description": "Agent Registration and Configuration",
    },
    {
        "name": "Agent",
        "description": "Agent Control, Sending Logs and Retrieving Logs",
    },
    {
        "name": "Beacon",
        "description": "Beacon Control, Sending Logs and Retrieving Logs",
    },
    {
        "name": "Middleware",
        "description": "Control over Middleware/Environment Settings",
    },
    {
        "name": "Script",
        "description": "Adding new scripts and script modules to the application that can be deployed to Agents",
    },
    {
        "name": "UI",
        "description": "Graphical UI Logic",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

origins = ["http://localhost", "http://localhost:9000"]

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        excluded_paths = ["/docs", "/redoc"]
        
        # Add security headers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Cache-Control'] = 'no-store, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response.headers['X-Robots-Tag'] = 'noindex'

       # Set CSP header only if the path is not excluded
        if request.url.path not in excluded_paths:
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; object-src 'none'"

        return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(SecurityHeadersMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/agent", CustomStaticFiles(directory="/agent"), name="agent")
templates = Jinja2Templates(directory="templates")


app.include_router(middleware.router, prefix="/api")
app.include_router(endpoints.router, prefix="/api")
app.include_router(beacons.router, prefix="/api")
app.include_router(agentlogs.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(agenttasks.router, prefix="/api")
app.include_router(scanprofiles.router, prefix="/api")
app.include_router(scripts.router, prefix="/api")


my_cmdout = {}
my_tasks = {}
my_reports = {}

API_KEY = os.environ.get(
    "APIKEY", str(uuid.uuid4())
)  # this basically prevents anyone not setting an APIKEY
API_KEY_NAME = "access_token"


@app.get("/", response_class=HTMLResponse, summary="Login Page", description="Displays the Login Page of the application", tags=["UI"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", summary="Authentication", description="Verifies authentication", tags=["UI"])
async def login(request: Request, api_key: str = Form(...)):
    if api_key == API_KEY:
        response = RedirectResponse(url="/main", status_code=302)
        response.set_cookie(key=API_KEY_NAME, value=api_key, secure=True, httponly=True)
        return response
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

@app.get("/logout", summary="Logout", description="Clears the authentication cookie", tags=["UI"])
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key=API_KEY_NAME)
    return response

@app.get("/main", summary="Authenticated area of the application", description="Authenticated part of the application", response_class=HTMLResponse, tags=["UI"])
async def main_page(request: Request, api_key: str = Depends(get_api_key)):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/template/{page_name}", response_class=HTMLResponse, summary="Load content of a page", description="Dynamic loading of authenticated pages in the application", tags=["UI"])
async def get_template(page_name: str, api_key: str = Depends(get_api_key)):
    try:
        return templates.TemplateResponse(f"{page_name}.html", {"request": {}})
    except TemplateNotFound:
        # Return the default template if the requested one is not found
        return templates.TemplateResponse("dashboard.html", {"request": {}})


# Custom OpenAPI function to include the security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="StealthGuardian API",
        version="1.0.0",
        description="This is the StealthGuardian API with API key authentication",
        routes=app.routes,
        tags=tags_metadata,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "StealthGuardianAPIKey": {
            "type": "apiKey",
            "name": "StealthGuardianAPIKey",
            "in": "header",
        },
        "StealthGuardianEndpointAPIKey": {
            "type": "apiKey",
            "name": "StealthGuardianEndpointAPIKey",
            "in": "header",
        },
    }
    openapi_schema["security"] = [
        {"StealthGuardianAPIKey": []},
        {"StealthGuardianEndpointAPIKey": []},
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
