"""Budget revision routes."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.dependencies import get_budget_or_404, require_budget_owner
from app.models import Budget, BudgetRevision, User
from app.schemas.budget import RevisionCreate, RevisionResponse

router = APIRouter(prefix="/budgets", tags=["revisions"])


@router.get("/{id}/revisions", response_model=list[RevisionResponse])
def list_revisions(
    id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """List all revisions for a budget."""
    budget = get_budget_or_404(db, id)
    require_budget_owner(budget, user)
    revisions = db.query(BudgetRevision).filter(BudgetRevision.budget_id == id).order_by(BudgetRevision.revision_number.desc()).all()
    return revisions


@router.post("/{id}/revisions", response_model=RevisionResponse, status_code=201)
def create_revision(
    id: str,
    body: RevisionCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create a revision snapshot for a budget."""
    budget = get_budget_or_404(db, id)
    require_budget_owner(budget, user)
    revision = BudgetRevision(
        budget_id=id,
        revision_number=body.revision_number,
        answers=body.answers,
        budget_data=body.budget_data,
    )
    db.add(revision)
    db.commit()
    db.refresh(revision)
    return revision
