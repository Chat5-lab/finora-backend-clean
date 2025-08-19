from routers.auth import router as auth_router
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from database import Base, engine
import models  # ensure models are imported so create_all sees them
from routers.accountant import router as accountant_router

from fastapi import FastAPI
app = FastAPI(
    title="Finora API",
    description="Effortless accounting, payroll, and insights — UK first, global ready",
    version="0.1.0",
)

# Root redirect to the interactive docs
@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")

# Health endpoint with build metadata (set in run.sh)
@app.get("/health")
def health():
    return {
        "status": "ok",
        "build_time": os.getenv("BUILD_TIME", "unknown"),
        "commit": os.getenv("GIT_COMMIT", "unknown"),
    }

# Create tables if missing (dev/SQLite)
Base.metadata.create_all(bind=engine)

# Feature routers
app.include_router(accountant_router)
app.include_router(auth_router)
