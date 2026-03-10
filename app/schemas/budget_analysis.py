"""Budget analysis request/response schemas."""
from typing import Optional

from pydantic import BaseModel


class Category(BaseModel):
    """Budget category with amount and percentage."""

    name: str
    amount: float
    percentage: float


class BudgetAnalysisRequest(BaseModel):
    """Request body for film budget analysis."""

    projectType: Optional[str] = None
    location: Optional[str] = None
    unionStatus: Optional[str] = None
    currency: Optional[str] = "USD"
    categories: list[Category]


class BudgetAnalysisResponse(BaseModel):
    """LLM analysis response - compatible with Lovable frontend."""

    narrative: str
    risks: list[str]
    recommendations: list[str]
