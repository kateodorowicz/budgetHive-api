"""Budget CRUD routes."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.dependencies import get_budget_or_404, require_budget_owner
from app.models import Budget, User
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """List all budgets for the current user."""
    budgets = db.query(Budget).filter(Budget.user_id == user.id).order_by(Budget.updated_at.desc()).all()
    return budgets


@router.post("", response_model=BudgetResponse, status_code=201)
def create_budget(
    body: BudgetCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create a new budget."""
    budget = Budget(
        user_id=user.id,
        name=body.name,
        answers=body.answers,
        budget_data=body.budget_data,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.patch("/{id}", response_model=BudgetResponse)
def update_budget(
    id: str,
    body: BudgetUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update a budget. Only provided fields are updated."""
    budget = get_budget_or_404(db, id)
    require_budget_owner(budget, user)
    if body.name is not None:
        budget.name = body.name
    if body.answers is not None:
        budget.answers = body.answers
    if body.budget_data is not None:
        budget.budget_data = body.budget_data
    db.commit()
    db.refresh(budget)
    return budget


@router.delete("/{id}", status_code=204)
def delete_budget(
    id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete a budget."""
    budget = get_budget_or_404(db, id)
    require_budget_owner(budget, user)
    db.delete(budget)
    db.commit()
    return None
