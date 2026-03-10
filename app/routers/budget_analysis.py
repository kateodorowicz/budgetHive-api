"""Budget analysis LLM endpoint."""
from fastapi import APIRouter, HTTPException

from app.schemas.budget_analysis import BudgetAnalysisRequest, BudgetAnalysisResponse
from app.services.llm_service import analyze_budget

router = APIRouter(prefix="/api", tags=["budget-analysis"])


@router.post(
    "/budget-analysis",
    response_model=BudgetAnalysisResponse,
    summary="Analyze film budget with LLM",
)
def post_budget_analysis(body: BudgetAnalysisRequest):
    """
    Analyze a film budget and return narrative, risks, and recommendations.
    Compatible with Lovable frontend.
    """
    try:
        return analyze_budget(body)
    except ValueError as e:
        msg = str(e)
        if "GEMINI_API_KEY" in msg or "not set" in msg:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key is not configured. Set GEMINI_API_KEY.",
            )
        if "Invalid JSON" in msg or "Empty response" in msg:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse LLM response. Please try again.",
            )
        raise HTTPException(status_code=500, detail=msg)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Budget analysis failed: {str(e)}",
        )
