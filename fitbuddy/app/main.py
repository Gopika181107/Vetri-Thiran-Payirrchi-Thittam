"""FastAPI entry point.  Run with:  uvicorn app.main:app --reload"""
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

init_db()
app.include_router(router)
