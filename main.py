import os
import sys
import types
import logging
from contextlib import asynccontextmanager

# Bootstrap the sys.path and sys.modules to allow execution from either backend/ or root folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# If 'backend' folder doesn't exist inside current_dir, map 'backend' module to current_dir
if not os.path.isdir(os.path.join(current_dir, "backend")):
    backend_module = types.ModuleType("backend")
    backend_module.__path__ = [current_dir]
    sys.modules["backend"] = backend_module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import auth, profile, skills, projects, education, certifications, experience, messages, custom_sections, job_applications

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("backend.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Connecting and checking database collections...")
    await init_db()
    yield
    # Shutdown tasks
    logger.info("Database connections closed.")

app = FastAPI(
    title="Portfolio Admin API",
    description="Asynchronous backend API for managing public portfolio details and contact inquiries.",
    version="1.0.0",
    lifespan=lifespan
)

# Allow CORS for dev server and preview apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(education.router, prefix="/api")
app.include_router(certifications.router, prefix="/api")
app.include_router(experience.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(custom_sections.router, prefix="/api")
app.include_router(job_applications.router, prefix="/api")

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "status": "online",
        "message": "Portfolio API is running successfully.",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Allow running directly via python -m backend.main
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
