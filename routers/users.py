from fastapi import APIRouter, Depends, Depends, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from database import get_db
from models import Membership, Organization
from routers.auth import get_current_user, User  # reuse existing dependency

from sqlalchemy import Table, MetaData, Column, Integer

# lightweight Core table for user_settings
metadata = MetaData()
user_settings = Table(
    "user_settings", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("active_org_id", Integer, nullable=True),
)

router = APIRouter(prefix="/users/me", tags=["users"])

class SetActiveIn(BaseModel):
    org_id: int

class OrgOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

@router.put("/orgs/active", response_model=OrgOut)
def set_active_org(body: SetActiveIn, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ensure the user is a member of this org
    member = db.execute(
        select(Membership).where(
            Membership.user_id == current.id,
            Membership.organization_id == body.org_id,
        )
    ).scalars().first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of that organization")

    # Upsert user_settings(user_id -> active_org_id)
    stmt = sqlite_insert(user_settings).values(user_id=current.id, active_org_id=body.org_id)
    stmt = stmt.on_conflict_do_update(
        index_elements=[user_settings.c.user_id],
        set_={"active_org_id": body.org_id},
    )
    db.execute(stmt)
    db.commit()

    org = db.execute(select(Organization).where(Organization.id == body.org_id)).scalars().first()
    return org

@router.get("/orgs/active", response_model=OrgOut)
def get_active_org(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.execute(
        select(user_settings.c.active_org_id).where(user_settings.c.user_id == current.id)
    ).first()
    if not row or not row[0]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active organization set")
    org_id = row[0]
    org = db.execute(select(Organization).where(Organization.id == org_id)).scalars().first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active organization not found")
    return org
