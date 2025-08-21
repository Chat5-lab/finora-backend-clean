from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status

def get_active_org_id(db: Session, user_id: int) -> int:
    """
    Resolve the user's active organization id.

    Order:
      1) user_settings.active_org_id
      2) First membership (supports common FK/relationship names)
    """
    # 1) user_settings (tests keep this up to date)
    row = db.execute(
        text("SELECT active_org_id FROM user_settings WHERE user_id = :uid"),
        {"uid": user_id},
    ).first()
    if row and row[0]:
        return int(row[0])

    # 2) fall back to membership
    from models import Membership  # local import to avoid circular import
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

    # Try common FK field names
    for fk in ("organization_id", "org_id", "business_id", "tenant_id"):
        if hasattr(mem, fk):
            org_id = getattr(mem, fk)
            if org_id:
                return int(org_id)

    # Or relationship names with .id
    for rel in ("organization", "org", "business", "tenant"):
        if hasattr(mem, rel):
            obj = getattr(mem, rel)
            if obj is not None and getattr(obj, "id", None):
                return int(obj.id)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot determine organization id",
    )
