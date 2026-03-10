"""Shared dependencies for authorization."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import Budget, DepartmentShare, User


def require_budget_owner(budget: Budget, user: User) -> Budget:
    """Raise 403 if user does not own the budget."""
    if budget.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this budget",
        )
    return budget


def get_budget_or_404(db: Session, budget_id: str) -> Budget:
    """Fetch budget by id or raise 404."""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


def get_share_or_404(db: Session, share_id: str) -> DepartmentShare:
    """Fetch share by id or raise 404."""
    share = db.query(DepartmentShare).filter(DepartmentShare.id == share_id).first()
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    return share
