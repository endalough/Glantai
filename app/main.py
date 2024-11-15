from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .core.database import create_db_and_tables
from .routers import dashboard
import logging


app = FastAPI()
app.include_router(dashboard.router)


logger = logging.getLogger(__name__)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

