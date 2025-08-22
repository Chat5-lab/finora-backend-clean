from datetime import date
from typing import Optional, Dict
from fastapi import APIRouter, Depends, Depends, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text  # <-- needed for raw SQL

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
def vat_preview(
    body: VatPreviewReq,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Resolve org: explicit or user's active org
    org_id = body.organization_id
    if org_id is None:
        row = db.execute(
            text("SELECT active_org_id FROM user_settings WHERE user_id = :u"),
            {"u": user.id},
        ).first()
        if not row or not row[0]:
            raise HTTPException(400, "No active organization for user and none provided.")
        org_id = int(row[0])

    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "Organization not found.")

    # Placeholder: return Boxes 1–9 as zero; real calc comes next
    boxes = {f"box{i}": 0.0 for i in range(1, 10)}
    return VatPreviewResp(boxes=boxes)
