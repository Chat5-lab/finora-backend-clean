from database import SessionLocal
from models import User, Organization, Membership
from passlib.hash import bcrypt

def set_first_attr(obj, names, value):
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return True
    return False

db = SessionLocal()
try:
    org = Organization(name="Café Demo")
    user = User(email="owner@example.com", hashed_password=bcrypt.hash("demo123"))
    db.add_all([org, user])
    db.flush()  # populate org.id and user.id

    m = Membership(role="owner")

    # Try FK column names first, then relationships
    if not set_first_attr(m, ("organization_id", "org_id", "business_id", "tenant_id"), org.id):
        if hasattr(m, "organization"):
            m.organization = org
        else:
            raise RuntimeError("Membership has no organization field/relationship")

    if not set_first_attr(m, ("user_id", "member_id"), user.id):
        if hasattr(m, "user"):
            m.user = user
        else:
            raise RuntimeError("Membership has no user field/relationship")

    db.add(m)
    db.commit()
    print("Seeded: Café Demo / owner@example.com : demo123")
finally:
    db.close()

# --- Seed minimal UK VAT rates if missing ---
from sqlalchemy import select
from models import TaxRate

existing_codes = {row[0] for row in db.execute(select(TaxRate.code)).all()}
seed_rates = [
    ("STD20", "UK Standard 20%", 20.00, "both"),
    ("RED5",  "UK Reduced 5%",    5.00, "both"),
    ("ZERO",  "Zero-rated 0%",    0.00, "both"),
    ("EXEMPT","Exempt",           0.00, "both"),
]
for code, name, rate, kind in seed_rates:
    if code not in existing_codes:
        db.add(TaxRate(code=code, name=name, rate=rate, kind=kind))
db.commit()
print("Seeded UK VAT rates (if missing).")
