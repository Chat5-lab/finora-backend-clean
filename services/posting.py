from decimal import Decimal
from datetime import date
from typing import Iterable
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Account, JournalEntry, JournalLine

class PostingError(ValueError): pass

def post_journal(db: Session, organization_id: int, when: date, memo: str | None, lines: Iterable[dict]) -> JournalEntry:
    deb = Decimal("0.00"); cred = Decimal("0.00")
    prepared = []
    for ln in lines:
        account_id = ln.get("account_id")
        account_code = ln.get("account_code")
        if not account_id and not account_code:
            raise PostingError("Each line must have account_id or account_code")
        q = select(Account).where(Account.organization_id==organization_id)
        q = q.where(Account.id==account_id) if account_id else q.where(Account.code==account_code)
        acct = db.execute(q).scalars().first()
        if not acct:
            raise PostingError("Account not found in this organization")
        d = Decimal(str(ln.get("debit", 0) or 0))
        c = Decimal(str(ln.get("credit", 0) or 0))
        if d < 0 or c < 0:
            raise PostingError("Amounts must be >= 0")
        if d > 0 and c > 0:
            raise PostingError("Line cannot have both debit and credit")
        deb += d; cred += c
        prepared.append((acct, d, c))
    if deb != cred or deb == Decimal("0.00"):
        raise PostingError("Journal not balanced")
    je = JournalEntry(organization_id=organization_id, date=when, memo=memo)
    db.add(je); db.flush()
    for acct, d, c in prepared:
        db.add(JournalLine(journal_entry_id=je.id, account_id=acct.id, debit=d, credit=c))
    db.commit(); db.refresh(je)
    return je
