from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.logging_config  # Initialize logging
from app.database import engine, Base
from app.scheduler import start_scheduler

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lucid API")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import briefings, goals, admin

app.include_router(briefings.router, prefix="/api/briefings", tags=["briefings"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.on_event("startup")
def on_startup():
    start_scheduler()
