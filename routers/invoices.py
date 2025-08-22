from decimal import Decimal
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Depends, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Customer, Invoice, InvoiceLine, Payment
from routers.auth import get_current_user
from routers.orgs import get_active_org_id

from pydantic import BaseModel, condecimal

router = APIRouter(prefix="/invoices", tags=["Invoices"])

# --- Schemas ---
class InvoiceLineIn(BaseModel):
    description: str
    quantity: condecimal(max_digits=10, decimal_places=3)
    unit_price: condecimal(max_digits=12, decimal_places=2)
    tax_rate: condecimal(max_digits=5, decimal_places=2) = Decimal("0.00")

class InvoiceCreateIn(BaseModel):
    customer_name: str
    customer_email: str | None = None
    issue_date: date
    due_date: date
    currency: str = "GBP"
    lines: List[InvoiceLineIn]

class InvoiceOut(BaseModel):
    id: int
    status: str
    net_total: condecimal(max_digits=12, decimal_places=2)
    tax_total: condecimal(max_digits=12, decimal_places=2)
    gross_total: condecimal(max_digits=12, decimal_places=2)

    class Config:
        from_attributes = True  # Pydantic v2: OK (or use model_config=ConfigDict(...))

def _sum_totals(lines: List[InvoiceLineIn]) -> tuple[Decimal, Decimal, Decimal]:
    net = Decimal("0.00")
    tax = Decimal("0.00")
    for l in lines:
        line_net = Decimal(l.quantity) * Decimal(l.unit_price)
        line_tax = (line_net * Decimal(l.tax_rate) / Decimal("100.00")).quantize(Decimal("0.01"))
        net += line_net
        tax += line_tax
    gross = net + tax
    return (net.quantize(Decimal("0.01")), tax.quantize(Decimal("0.01")), gross.quantize(Decimal("0.01")))

@router.post("", response_model=InvoiceOut)
def create_invoice(
    payload: InvoiceCreateIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    org_id: int = Depends(get_active_org_id),
):
    # find or create customer
    cust = db.execute(
        select(Customer).where(Customer.organization_id == org_id, Customer.email == payload.customer_email)
    ).scalar_one_or_none()
    if not cust:
        cust = Customer(organization_id=org_id, name=payload.customer_name, email=payload.customer_email)
        db.add(cust)
        db.flush()

    net, tax, gross = _sum_totals(payload.lines)
    inv = Invoice(
        organization_id=org_id,
        customer_id=cust.id,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        currency=payload.currency,
        status="draft",
        net_total=net,
        tax_total=tax,
        gross_total=gross,
    )
    db.add(inv)
    db.flush()

    for l in payload.lines:
        db.add(
            InvoiceLine(
                invoice_id=inv.id,
                description=l.description,
                quantity=Decimal(l.quantity),
                unit_price=Decimal(l.unit_price),
                tax_rate=Decimal(l.tax_rate),
            )
        )

    db.commit()
    db.refresh(inv)
    return inv

class MarkPaidIn(BaseModel):
    date: date
    amount: condecimal(max_digits=12, decimal_places=2)

@router.post("/{invoice_id}/mark_paid")
def mark_paid(
    invoice_id: int,
    payload: MarkPaidIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    org_id: int = Depends(get_active_org_id),
):
    inv = db.get(Invoice, invoice_id)
    if not inv or inv.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # record payment
    pay = Payment(
        organization_id=org_id,
        invoice_id=invoice_id,
        date=payload.date,
        amount=Decimal(payload.amount),
        method="manual",
        reference=f"INV-{invoice_id}",
    )
    db.add(pay)

    # Post to ledger (import inside function to avoid circulars)
    try:
        from routers.ledger import post_journal
        lines = [
            {"account_code": "1000", "debit": str(payload.amount)},
            {"account_code": "1100", "credit": str(payload.amount)},
        ]
        post_journal(
            {"date": str(payload.date), "memo": f"Payment for invoice {invoice_id}", "lines": lines},
            db=db, user=user, org_id=org_id,  # type: ignore
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ledger post failed: {e}")

    inv.status = "paid"
    db.commit()
    return {"ok": True, "invoice_id": invoice_id}