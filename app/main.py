from fastapi import FastAPI

from .core.database import create_db_and_tables
from .routers import items
import logging


app = FastAPI()
app.include_router(items.router)


logger = logging.getLogger(__name__)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

