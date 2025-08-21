from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class AccountantPermissions(BaseModel):
    view: bool = True
    file_tax: bool = False

class AccountantBase(BaseModel):
    firm_name: str = Field(..., max_length=200)
    contact_name: str = Field(..., max_length=200)
    email: EmailStr
    phone: Optional[str] = ""
    website: Optional[str] = None
    notes: Optional[str] = ""
    permissions: AccountantPermissions = AccountantPermissions()

class AccountantCreate(AccountantBase):
    business_id: int = 1

class AccountantOut(AccountantBase):
    id: int
    business_id: int
    status: str
    class Config:
        from_attributes = True

class InviteOut(BaseModel):
    invite_url: str

class AcceptInviteIn(BaseModel):
    token: str

# --- generic response model used by several routers ---
from pydantic import BaseModel

class Message(BaseModel):
    detail: str
