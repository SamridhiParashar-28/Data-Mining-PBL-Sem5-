import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.config import STATIC_DIR, TEMPLATES_DIR
from app.database import init_db, seed_demo_user
from app.ml_pipeline.pipeline_manager import pipeline_manager
from app.routers import (
    auth_router,
    employee_router,
    analysis_router,
    pipeline_router,
    admin_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("[Server] Initializing SQLite database...")
    init_db()
    seed_demo_user()
    print("[Server] Initializing Data Mining Pipeline...")
    pipeline_manager.initialize()
    print("[Server] Pipeline is ready. Server operational.")
    yield
    print("[Server] Shutting down...")

app = FastAPI(
    title="Employee Performance & Prediction Pipeline",
    description="Full-Stack Data Mining & Machine Learning Pipeline Web Application",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include Routers
app.include_router(auth_router.router)
app.include_router(employee_router.router)
app.include_router(analysis_router.router)
app.include_router(pipeline_router.router)
app.include_router(admin_router.router)

# Frontend Page Routes
@app.get("/", response_class=HTMLResponse)
async def serve_landing():
    return FileResponse(TEMPLATES_DIR / "index.html")

@app.get("/signup", response_class=HTMLResponse)
async def serve_signup():
    return FileResponse(TEMPLATES_DIR / "signup.html")

@app.get("/signin", response_class=HTMLResponse)
async def serve_signin():
    return FileResponse(TEMPLATES_DIR / "signin.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    return FileResponse(TEMPLATES_DIR / "dashboard.html")

@app.get("/pipeline", response_class=HTMLResponse)
async def serve_pipeline():
    return FileResponse(TEMPLATES_DIR / "pipeline.html")

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin():
    return FileResponse(TEMPLATES_DIR / "admin.html")
