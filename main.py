from fastapi import FastAPI
from database import Base, engine
from routers.accountant import router as accountant_router

app = FastAPI(
    title="Finora API",
    description="Effortless accounting, payroll, and insights — UK first, global ready",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(accountant_router)
