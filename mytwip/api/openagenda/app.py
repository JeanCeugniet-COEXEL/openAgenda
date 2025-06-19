from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, Depends, Request
from mytwip.core.openagenda import core
from mytwip.core.openagenda.core import *
from mytwip.utils.common import *
from mytwip.utils.security import rate_limit
import json

# Setup application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events"""
    global logger
    # Startup
    openagenda_cached_query_cleanup()
    logger = logger_init()
    logger.info("Parsing API starting up")

    yield  # This is where the application runs
    
    # Shutdown
    logger.info("Parsing API shutting down")

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="MyTwip OpenAgenda API",
    description="API for parsing OpenAgenda agendas and avents",
    version="1.0.0",
)

@app.get("/")
async def root(request: Request, api_key: str = Depends(rate_limit)):
    """
    Current API Status
    """
    logger.info("@/")
    return {"name": __name__, "status": "live"}

@app.get("/agendas/search/{search_term}")
async def agendas_search(request: Request, api_key: str = Depends(rate_limit), search_term: str = ""):
    """
    Search for OpenAgenda agendas by search term.
    - **search_term**: Search term. WARNING : OpenAgenda platform is apparently case sensitive.
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    search_term = search_term.strip()
    result = core.agendas_search(search_term)
        
    return result

@app.get("/agendas/by_slug/{agenda_slug}")
async def agendas_by_slug(request: Request, api_key: str = Depends(rate_limit), agenda_slug: str = ""):
    """
    Search for OpenAgenda agendas by slug
    - **agenda_slug**: The slug of this agenda on the OpenAgenda platform. SHOULD be unique.
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    agenda_slug = agenda_slug.strip()
    result = core.agendas_by_slug(agenda_slug)
        
    return result

@app.get("/agendas/details/{agenda_uid}")
async def agendas_details(request: Request, api_key: str = Depends(rate_limit), agenda_uid: int|None = None):
    """
    Search for OpenAgenda agendas by uid
    - **agena_uid**: The ID of this agenda on the OpenAgenda platform.
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.agendas_details(agenda_uid)
        
    return result

@app.get("/events/by_agenda_uid/{agenda_uid}")
async def events_by_agenda_uid(request: Request, api_key: str = Depends(rate_limit), agenda_uid: int|None = None):
    """
    Search for OpenAgenda events by agenda uid
    - **agenda_uid**: The ID of the agenda for which you want to retrieve the events.
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.events_by_agenda_uid(agenda_uid)
        
    return result

@app.get("/cache_query_cleanup")
async def cache_query_cleanup(request: Request, api_key: str = Depends(rate_limit), force: bool = False):
    """
    Cleanup or reset query cache
    - **force**: If specified and true, forces a full reset of the OpenAgenda queries cache.
    """
    result = openagenda_cached_query_cleanup(force)

    return result

