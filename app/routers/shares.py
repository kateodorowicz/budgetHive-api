"""Department share routes."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.dependencies import get_budget_or_404, get_share_or_404, require_budget_owner
from app.models import Budget, DepartmentShare, User
from app.schemas.budget import ShareCreate, ShareResponse, ShareUpdate

router = APIRouter(tags=["shares"])


@router.post("/budgets/{id}/shares", response_model=ShareResponse, status_code=201)
def create_share(
    id: str,
    body: ShareCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create a share for a budget."""
    budget = get_budget_or_404(db, id)
    require_budget_owner(budget, user)
    share = DepartmentShare(
        budget_id=id,
        share_type=body.share_type,
        permissions=body.permissions,
        expires_at=body.expires_at,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


@router.get("/shares/{share_id}", response_model=ShareResponse)
def get_share(
    share_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get a share by id. User must own the budget."""
    share = get_share_or_404(db, share_id)
    require_budget_owner(share.budget, user)
    return share


@router.patch("/shares/{share_id}", response_model=ShareResponse)
def update_share(
    share_id: str,
    body: ShareUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update a share. User must own the budget."""
    share = get_share_or_404(db, share_id)
    require_budget_owner(share.budget, user)
    if body.share_type is not None:
        share.share_type = body.share_type
    if body.permissions is not None:
        share.permissions = body.permissions
    if body.expires_at is not None:
        share.expires_at = body.expires_at
    db.commit()
    db.refresh(share)
    return share
