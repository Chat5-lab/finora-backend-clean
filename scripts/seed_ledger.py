from sqlalchemy import select
from database import SessionLocal
from models import Organization, Account

DEFAULTS = [
    ("1000", "Cash", "asset"),
    ("1200", "Bank", "asset"),
    ("2000", "Sales", "income"),
    ("2200", "VAT Payable", "liability"),
    ("5000", "Expenses", "expense"),
]

db = SessionLocal()
org = db.execute(select(Organization)).scalars().first()
if not org:
    print("No org found; run scripts/seed.py first")
else:
    created = 0
    for code, name, typ in DEFAULTS:
        exists = db.execute(
            select(Account).where(Account.organization_id==org.id, Account.code==code)
        ).scalars().first()
        if not exists:
            db.add(Account(organization_id=org.id, code=code, name=name, type=typ))
            created += 1
    db.commit()
    print(f"Seeded {created} accounts for org {org.name} (id={org.id})")
db.close()
