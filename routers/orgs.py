from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Organization, Membership, User
from routers.auth import get_current_user

router = APIRouter(prefix="/orgs", tags=["orgs"])

@router.post("/", response_model=dict, status_code=201)
def create_org(name: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exists = db.query(Organization).filter(Organization.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Organization name already exists")
    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    # add creator as owner
    membership = Membership(user_id=user.id, org_id=org.id, role="owner")
    db.add(membership)
    db.commit()
    return {"id": org.id, "name": org.name}

@router.get("/", response_model=List[dict])
def list_my_orgs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = (
        db.query(Organization)
        .join(Membership, Membership.org_id == Organization.id)
        .filter(Membership.user_id == user.id)
        .all()
    )
    return [{"id": o.id, "name": o.name} for o in q]
