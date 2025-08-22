from fastapi import APIRouter, Depends, Depends, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas import AccountantCreate, AccountantOut, InviteOut, AcceptInviteIn
from crud import upsert_accountant, get_accountant_for_business, set_status, get_by_token

router = APIRouter(prefix="/accountant", tags=["Accountant"])

@router.get("", response_model=AccountantOut)
def get_accountant(business_id: int = 1, db: Session = Depends(get_db)):
    acct = get_accountant_for_business(db, business_id)
    if not acct:
        raise HTTPException(status_code=404, detail="No accountant on file")
    return acct

@router.post("", response_model=AccountantOut)
def create_or_update_accountant(payload: AccountantCreate, db: Session = Depends(get_db)):
    acct = upsert_accountant(db, payload)
    return acct

@router.post("/invite", response_model=InviteOut)
def invite_accountant(business_id: int = 1, request: Request = None, db: Session = Depends(get_db)):
    acct = get_accountant_for_business(db, business_id)
    if not acct:
        raise HTTPException(status_code=404, detail="No accountant on file to invite")
    set_status(db, business_id, "invited")
    base = str(request.base_url).rstrip("/")
    invite_url = f"{base}/accountant/accept?token={acct.invite_token}"
    return InviteOut(invite_url=invite_url)

@router.post("/accept", response_model=AccountantOut)
def accept_invite(body: AcceptInviteIn, db: Session = Depends(get_db)):
    acct = get_by_token(db, body.token)
    if not acct:
        raise HTTPException(status_code=400, detail="Invalid or expired invite token")
    set_status(db, acct.business_id, "active")
    return acct

@router.post("/revoke", response_model=AccountantOut)
def revoke_access(business_id: int = 1, db: Session = Depends(get_db)):
    acct = set_status(db, business_id, "revoked")
    if not acct:
        raise HTTPException(status_code=404, detail="No accountant on file")
    return acct
