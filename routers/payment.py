from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/ping", summary="Payments service ping")
def ping():
    return {"status": "ok"}
