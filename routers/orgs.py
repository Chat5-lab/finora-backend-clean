from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from fastapi import Depends
from sqlalchemy.orm import Session

def get_active_org_id(db: Session = Depends(get_db), user=Depends(get_current_user)) -> int:
    """
    Resolve the user's active organization id.

    Order:
      1) user_settings.active_org_id (if present)
      2) First membership org (supports various FK/relationship names)
    """
    # 1) Try user_settings table (tests create/seed this)
    row = db.execute(
        text("SELECT active_org_id FROM user_settings WHERE user_id = :uid"),
        {"uid": user_id},
    ).first()
    if row and row[0]:
        return int(row[0])

    # 2) Fall back to membership
    from models import Membership  # local import to avoid cycles

    mem = (
        db.query(Membership)
        .filter(Membership.user_id == user_id)
        .order_by(Membership.id.asc())
        .first()
    )
    if not mem:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization for user",
        )

    # Try common foreign key field names
    for fk in ("organization_id", "org_id", "business_id", "tenant_id"):
        if hasattr(mem, fk):
            org_id = getattr(mem, fk)
            if org_id:
                return int(org_id)

    # Try relationship names with .id
    for rel in ("organization", "org", "business", "tenant"):
        if hasattr(mem, rel):
            obj = getattr(mem, rel)
            if obj is not None and getattr(obj, "id", None):
                return int(obj.id)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot determine organization id",
    )
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import Organization, Membership
from routers.auth import get_current_user, User  # reuse the dependency

router = APIRouter(prefix="/orgs", tags=["orgs"])

class OrgOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

def _detect_fk(colnames, candidates):
    for c in candidates:
        if c in colnames:
            return c
    return None

@router.get("/me", response_model=list[OrgOut])
def my_orgs(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    M = Membership.__table__
    cols = set(M.c.keys())
    user_fk = _detect_fk(cols, ("user_id","member_id"))
    org_fk  = _detect_fk(cols, ("organization_id","org_id","business_id","tenant_id"))
    if not user_fk or not org_fk:
        # Fallback: try ORM relationship join via attribute names
        q = db.query(Organization).join(Membership).filter(
            getattr(Membership, "user_id", None) == current.id  # may be None, SQLA ignores
        )
        return q.all()

    stmt = (
        select(Organization)
        .join(M, Organization.id == M.c[org_fk])
        .where(M.c[user_fk] == current.id)
    )
    return db.execute(stmt).scalars().all()