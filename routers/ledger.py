from decimal import Decimal
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Depends, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, Table, Column, Integer, MetaData
from database import get_db
from models import Account, Membership
from routers.auth import get_current_user, User
from services.posting import post_journal, PostingError

metadata = MetaData()
user_settings = Table(
    "user_settings", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("active_org_id", Integer),
)

router = APIRouter(prefix="/ledger", tags=["ledger"])

class AccountOut(BaseModel):
    id: int
    code: str
    name: str
    type: str
    class Config:
        from_attributes = True

class LineIn(BaseModel):
    account_id: Optional[int] = None
    account_code: Optional[str] = None
    debit: Decimal = Field(default=0)
    credit: Decimal = Field(default=0)

class JournalIn(BaseModel):
    date: date
    memo: Optional[str] = None
    lines: List[LineIn]

class JournalOut(BaseModel):
    id: int
    date: date
    memo: Optional[str] = None
    class Config:
        from_attributes = True

def _active_org_id(user_id: int, db: Session = Depends(get_db)):
    row = db.execute(select(user_settings.c.active_org_id).where(user_settings.c.user_id==user_id)).first()
    if row and row[0]:
        return int(row[0])
    return db.execute(select(Membership.organization_id).where(Membership.user_id==user_id)).scalar()

@router.get("/accounts", response_model=list[AccountOut])
def list_accounts(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = _active_org_id(current.id, db)
    if not org_id:
        return []
    rows = db.execute(select(Account).where(Account.organization_id==org_id).order_by(Account.code)).scalars().all()
    return rows

@router.post("/journals", response_model=JournalOut, status_code=201)
def create_journal(payload: JournalIn, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = _active_org_id(current.id, db)
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No organization available")
    try:
        je = post_journal(
            db, organization_id=org_id, when=payload.date, memo=payload.memo,
            lines=[ln.model_dump() for ln in payload.lines]
        )
    except PostingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return je
