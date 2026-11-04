import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
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

# Global startup state flag
_pipeline_ready = False
_pipeline_error = None

def _init_pipeline_background():
    """Runs ML pipeline initialization in a background thread so the
    HTTP server starts accepting connections immediately."""
    global _pipeline_ready, _pipeline_error
    try:
        print("[Server] Background: Initializing Data Mining Pipeline...")
        pipeline_manager.initialize()
        _pipeline_ready = True
        print("[Server] Background: ML Pipeline ready!")
    except Exception as e:
        _pipeline_error = str(e)
        print(f"[Server] Background: Pipeline initialization failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB init is fast - run synchronously
    print("[Server] Initializing SQLite database...")
    init_db()
    seed_demo_user()
    print("[Server] Database ready. Launching ML pipeline in background thread...")
    # Launch ML training in background - server is immediately available
    t = threading.Thread(target=_init_pipeline_background, daemon=True)
    t.start()
    print("[Server] HTTP server is READY. Browser can open now.")
    print("[Server] ML Pipeline training in background (~30-60s)...")
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
@app.get("/api/status")
async def get_server_status():
    """Fast health-check endpoint - used by browser to poll pipeline readiness."""
    return JSONResponse({
        "server": "ok",
        "pipeline_ready": _pipeline_ready,
        "pipeline_error": _pipeline_error
    })

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
