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
    logger.info("/agendas/search/%s", search_term)
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
    logger.info("/agendas/by_slug/%s", agenda_slug)
    result = {"status": "unknown", "msg": "Unkown status"}
    agenda_slug = agenda_slug.strip()
    result = core.agendas_by_slug(agenda_slug)
        
    return result

@app.get("/agendas/details/{agenda_uid}")
async def agendas_details(request: Request, api_key: str = Depends(rate_limit), agenda_uid: int|None = None):
    """
    Search for OpenAgenda agendas by uid
    - **agenda_uid**: The ID of this agenda on the OpenAgenda platform.
    """
    logger.info("/agendas/details/%s", agenda_uid)
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.agendas_details(agenda_uid)
        
    return result

@app.get("/agendas/with_events/{agenda_uid}")
async def agendas_with_events(request: Request, api_key: str = Depends(rate_limit), agenda_uid: int|None = None):
    """
    Search for OpenAgenda agendas by uid, with its events
    - **agenda_uid**: The ID of this agenda on the OpenAgenda platform.
    """
    logger.info("/agendas/with_events/%s", agenda_uid)
    result = {"status": "unknown", "msg": "Unkown status"}
    agenda_result = core.agendas_details(agenda_uid)
    events_result = core.events_by_agenda_uid(agenda_uid)
    result["status"] = "success" if (agenda_result.get("status", "failure") == "success" and events_result.get("status", "failure") == "success") else "failure"
    result["msg"] = f"Agenda : {agenda_result.get("msg") if "msg" in agenda_result else "No msg"}. Events : {events_result.get("msg") if "msg" in events_result else "No msg"}.".replace("..", ".")
    result["data"] = {
        "agenda": agenda_result.get("data", {}).get("agenda", None),
        "events" : events_result.get("data", {}).get("events", []),
        "events_total": events_result.get("data", {}).get("total", 0),
        "events_pages": events_result.get("data", {}).get("pages", 0)
    }
    
    return result

@app.get("/events/by_agenda_uid/{agenda_uid}")
async def events_by_agenda_uid(request: Request, api_key: str = Depends(rate_limit), agenda_uid: int|None = None):
    """
    Search for OpenAgenda events by agenda uid
    - **agenda_uid**: The ID of the agenda for which you want to retrieve the events.
    """
    logger.info("/events/by_agenda_uid/%s", agenda_uid)
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.events_by_agenda_uid(agenda_uid)
        
    return result

@app.get("/cache_query_cleanup")
async def cache_query_cleanup(request: Request, api_key: str = Depends(rate_limit), force: bool = False):
    """
    Cleanup or reset query cache
    - **force**: If specified and true, forces a full reset of the OpenAgenda queries cache.
    """
    logger.info("/cache_query_cleanup/%s", force)
    result = openagenda_cached_query_cleanup(force)

    return result

