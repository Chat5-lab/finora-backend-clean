from sqlalchemy import String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import secrets
from database import Base

class AccountantContact(Base):
    __tablename__ = "accountant_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(Integer, index=True)
    firm_name: Mapped[str] = mapped_column(String(200))
    contact_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[str] = mapped_column(String(50), default="")
    website: Mapped[str] = mapped_column(String(255), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    can_view: Mapped[bool] = mapped_column(Boolean, default=True)
    can_file_tax: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="invited")
    invite_token: Mapped[str] = mapped_column(String(64), default=lambda: secrets.token_urlsafe(24))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---------- Auth & Orgs ----------
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    members = relationship("Membership", back_populates="organization", cascade="all, delete-orphan")

class Membership(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_id  = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role    = Column(String(50), default="owner", nullable=False)

    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="members")
    __table_args__ = (UniqueConstraint("user_id", "org_id", name="uq_user_org"),)
# --- Ledger models ---
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # asset/liability/equity/income/expense
    __table_args__ = (UniqueConstraint('organization_id', 'code', name='uq_account_org_code'),)
    organization = relationship("Organization", backref="accounts")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    memo = Column(String(255), nullable=True)
    lines = relationship("JournalLine", cascade="all, delete-orphan", backref="journal")

class JournalLine(Base):
    __tablename__ = "journal_lines"
    id = Column(Integer, primary_key=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    debit = Column(Numeric(12,2), nullable=False, default=0)
    credit = Column(Numeric(12,2), nullable=False, default=0)
    __table_args__ = (CheckConstraint('NOT (debit > 0 AND credit > 0)', name='ck_line_not_both'),)
    account = relationship("Account")

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base  # already present earlier in the file

class UserSettings(Base):
    __tablename__ = "user_settings"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    active_org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    user = relationship("User", backref="settings", uselist=False)
    active_org = relationship("Organization")

# --- VAT models (minimal scaffold) ---
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship

class VatScheme(Base):
    __tablename__ = "vat_schemes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # optional org scoping
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization")

class TaxRate(Base):
    __tablename__ = "tax_rates"
    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, unique=True)  # e.g., "STD20", "RED5", "ZERO", "EXEMPT"
    name = Column(String, nullable=False)               # human friendly name
    rate = Column(Numeric(5,2), nullable=False)         # percentage e.g., 20.00
    kind = Column(String, nullable=False, default="sale")  # sale|purchase|both
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization")

class VatPeriod(Base):
    __tablename__ = "vat_periods"
    id = Column(Integer, primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="open")  # open|submitted|paid
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
