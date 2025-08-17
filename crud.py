from sqlalchemy.orm import Session
from typing import Optional
from models import AccountantContact
from schemas import AccountantCreate

def get_accountant_for_business(db: Session, business_id: int) -> Optional[AccountantContact]:
    return db.query(AccountantContact).filter(AccountantContact.business_id == business_id).first()

def upsert_accountant(db: Session, data: AccountantCreate) -> AccountantContact:
    acct = get_accountant_for_business(db, data.business_id)
    if not acct:
        acct = AccountantContact(business_id=data.business_id,
                                 firm_name=data.firm_name,
                                 contact_name=data.contact_name,
                                 email=data.email)
        db.add(acct)
    acct.firm_name = data.firm_name
    acct.contact_name = data.contact_name
    acct.email = data.email
    acct.phone = data.phone or ""
    acct.website = data.website or ""
    acct.notes = data.notes or ""
    acct.can_view = data.permissions.view
    acct.can_file_tax = data.permissions.file_tax
    db.commit()
    db.refresh(acct)
    return acct

def set_status(db: Session, business_id: int, status: str) -> Optional[AccountantContact]:
    acct = get_accountant_for_business(db, business_id)
    if not acct:
        return None
    acct.status = status
    db.commit()
    db.refresh(acct)
    return acct

def get_by_token(db: Session, token: str) -> Optional[AccountantContact]:
    return db.query(AccountantContact).filter(AccountantContact.invite_token == token).first()
