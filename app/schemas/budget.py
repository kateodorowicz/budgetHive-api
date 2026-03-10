"""Budget schemas."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class BudgetCreate(BaseModel):
    name: Optional[str] = None
    answers: Optional[dict] = None
    budget_data: Optional[dict] = None


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    answers: Optional[dict] = None
    budget_data: Optional[dict] = None


class BudgetResponse(BaseModel):
    id: str
    user_id: str
    name: Optional[str]
    answers: Optional[dict]
    budget_data: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    action: str
    details: Optional[dict] = None


class ActivityResponse(BaseModel):
    id: str
    budget_id: str
    action: str
    details: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class RevisionCreate(BaseModel):
    revision_number: int
    answers: Optional[dict] = None
    budget_data: Optional[dict] = None


class RevisionResponse(BaseModel):
    id: str
    budget_id: str
    revision_number: int
    answers: Optional[dict]
    budget_data: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class ShareCreate(BaseModel):
    share_type: Optional[str] = None
    permissions: Optional[dict] = None
    expires_at: Optional[datetime] = None


class ShareUpdate(BaseModel):
    share_type: Optional[str] = None
    permissions: Optional[dict] = None
    expires_at: Optional[datetime] = None


class ShareResponse(BaseModel):
    id: str
    budget_id: str
    share_type: Optional[str]
    permissions: Optional[dict]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
