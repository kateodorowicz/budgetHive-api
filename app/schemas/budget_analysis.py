"""Budget analysis request/response schemas."""
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, model_validator


class Category(BaseModel):
    """Budget category. Accepts 'total' (Lovable) or 'amount' (legacy)."""

    name: str
    code: Optional[str] = None
    amount: float = Field(
        description="Budget amount; accepts 'total' or 'amount' from client",
        validation_alias=AliasChoices("total", "amount"),
    )
    percentage: float


class BudgetAnalysisRequest(BaseModel):
    """Request body for film budget analysis. Accepts Lovable snake_case and legacy camelCase."""

    # Lovable frontend fields
    project_name: Optional[str] = None
    project_type: Optional[str] = None
    shoot_days: Optional[str] = None
    grand_total: Optional[float] = None
    health_score: Optional[float] = None
    # Legacy / alternate
    projectType: Optional[str] = None
    location: Optional[str] = None
    unionStatus: Optional[str] = None
    currency: Optional[str] = "USD"
    categories: list[Category]

    @model_validator(mode="after")
    def normalize_for_llm(self):
        """Ensure projectType is set from project_type if needed."""
        if self.projectType is None and self.project_type is not None:
            object.__setattr__(self, "projectType", self.project_type)
        return self


class BudgetAnalysisResponse(BaseModel):
    """LLM analysis response - compatible with Lovable frontend."""

    narrative: str
    risks: list[str]
    recommendations: list[str]
