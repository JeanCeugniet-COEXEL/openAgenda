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
    Search for OpenAgenda agendas by search term
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.agendas_search(search_term)
        
    return result

@app.get("/agendas/by_slug/{agenda_slug}")
async def agendas_by_slug(request: Request, api_key: str = Depends(rate_limit), agenda_slug: str = ""):
    """
    Search for OpenAgenda agendas by slug
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.agendas_by_slug(agenda_slug)
        
    return result

@app.get("/agendas/details/{agenda_uid}")
async def agendas_details(request: Request, api_key: str = Depends(rate_limit), agenda_uid: int|None = None):
    """
    Search for OpenAgenda agendas by uid
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.agendas_details(agenda_uid)
        
    return result

@app.get("/events/by_agenda_uid/{agenda_uid}")
async def events_by_agenda_uid(request: Request, api_key: str = Depends(rate_limit), agenda_uid: int|None = None):
    """
    Search for OpenAgenda events by agenda uid
    """
    result = {"status": "unknown", "msg": "Unkown status"}
    result = core.events_by_agenda_uid(agenda_uid)
        
    return result

