from datetime import date
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import User, Organization
from routers.auth import get_current_user

router = APIRouter(prefix="/vat", tags=["VAT"])

class VatPreviewReq(BaseModel):
    period_start: date = Field(..., description="Start date (inclusive)")
    period_end: date = Field(..., description="End date (inclusive)")
    organization_id: Optional[int] = None

class VatPreviewResp(BaseModel):
    boxes: Dict[str, float]

@router.post("/preview", response_model=VatPreviewResp)
def vat_preview(body: VatPreviewReq, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Resolve org: explicit or user's active org (from user_settings)
    org_id = body.organization_id
    if org_id is None:
        active = db.execute(
            "SELECT active_org_id FROM user_settings WHERE user_id = :u",
            {"u": user.id}
        ).fetchone()
        if not active or not active[0]:
            raise HTTPException(400, "No active organization for user and none provided.")
        org_id = int(active[0])

    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "Organization not found.")

    # TODO: compute from journals/lines and tax rates.
    # For now, return valid shape with zeros so UI and tests can proceed.
    boxes = {f"box{i}": 0.0 for i in range(1, 10)}
    return VatPreviewResp(boxes=boxes)
