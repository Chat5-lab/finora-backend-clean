from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/bank", tags=["Bank"])

class OAuthStartRequest(BaseModel):
    provider_id: str

class SyncRequest(BaseModel):
    since: Optional[str] = None

@router.get("/providers")
def list_providers() -> List[Dict[str, Any]]:
    return [{"id": "demo", "name": "Demo Bank", "scopes": ["accounts", "transactions"]}]

@router.get("/accounts")
def list_accounts() -> List[Dict[str, Any]]:
    return []

@router.post("/oauth/start", status_code=201)
def oauth_start(req: OAuthStartRequest) -> Dict[str, str]:
    if req.provider_id != "demo":
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"auth_url": "https://example.com/oauth/authorize?provider=demo&state=stub"}

@router.post("/transactions:sync")
def transactions_sync(req: SyncRequest) -> Dict[str, Any]:
    return {"synced": 0, "cursor": None}
