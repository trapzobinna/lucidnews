from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import app.logging_config
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lucid API")

# CORS — allow local dev + production frontend
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import briefings, goals, admin

app.include_router(briefings.router, prefix="/api/briefings", tags=["briefings"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def root():
    return {"message": "Lucid API is running"}

# Only start scheduler in full mode (skip on API-only deploys)
if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
    from app.scheduler import start_scheduler

    @app.on_event("startup")
    def on_startup():
        start_scheduler()
