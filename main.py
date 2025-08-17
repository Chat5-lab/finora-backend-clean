from fastapi import FastAPI
from database import Base, engine
from routers.accountant import router as accountant_router

app = FastAPI(
    title="Finora API",
    description="Effortless accounting, payroll, and insights — UK first, global ready",
    version="0.1.0",
)
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/docs")
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(accountant_router)

