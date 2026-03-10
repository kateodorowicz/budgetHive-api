"""Activity routes for budgets."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.dependencies import get_budget_or_404, require_budget_owner
from app.models import Activity, Budget, User
from app.schemas.budget import ActivityCreate, ActivityResponse

router = APIRouter(prefix="/budgets", tags=["activities"])


@router.get("/{id}/activities", response_model=list[ActivityResponse])
def list_activities(
    id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """List all activities for a budget."""
    budget = get_budget_or_404(db, id)
    require_budget_owner(budget, user)
    activities = db.query(Activity).filter(Activity.budget_id == id).order_by(Activity.created_at.desc()).all()
    return activities


@router.post("/{id}/activities", response_model=ActivityResponse, status_code=201)
def create_activity(
    id: str,
    body: ActivityCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create an activity for a budget."""
    budget = get_budget_or_404(db, id)
    require_budget_owner(budget, user)
    activity = Activity(
        budget_id=id,
        action=body.action,
        details=body.details,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
