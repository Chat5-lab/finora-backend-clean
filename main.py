from routers.ledger import router as ledger_router
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routers.auth import router as auth_router
from routers.orgs import router as orgs_router
from routers.accountant import router as accountant_router

# Optional: active-org endpoints (only if file exists)
try:
    from routers.users import router as users_router
except Exception:
    users_router = None  # fine if it's not there yet

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

# Routers
app.include_router(accountant_router)
app.include_router(auth_router)
app.include_router(orgs_router)
if users_router:
    app.include_router(users_router)
app.include_router(ledger_router)
from routers.vat import router as vat_router
app.include_router(vat_router)
from routers.bank import router as bank_router
app.include_router(bank_router)
from routers.payment import router as payment_router
app.include_router(payment_router)
from routers.invoices import router as invoices_router
app.include_router(invoices_router)
