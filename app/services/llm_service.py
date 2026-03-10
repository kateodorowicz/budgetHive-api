"""LLM service for budget analysis using OpenAI."""
import json
import re
from openai import OpenAI

from app.config import settings
from app.schemas.budget_analysis import BudgetAnalysisRequest, BudgetAnalysisResponse


def _build_prompt(req: BudgetAnalysisRequest) -> str:
    """Build a structured prompt from the request."""
    lines = [
        "Analyze this film production budget and provide a professional assessment.",
        "",
        "## Budget summary",
    ]
    total = sum(c.amount for c in req.categories)
    for cat in req.categories:
        lines.append(f"- {cat.name}: {req.currency or 'USD'} {cat.amount:,.2f} ({cat.percentage:.1f}%)")
    lines.append(f"\nTotal: {req.currency or 'USD'} {total:,.2f}")
    if req.projectType:
        lines.append(f"\nProject type: {req.projectType}")
    if req.location:
        lines.append(f"Location: {req.location}")
    if req.unionStatus:
        lines.append(f"Union status: {req.unionStatus}")
    lines.append(
        """
Respond with valid JSON only, no markdown or extra text. Use this exact structure:
{
  "narrative": "A 2-4 sentence analysis of the budget structure and appropriateness.",
  "risks": ["risk1", "risk2", "..."],
  "recommendations": ["rec1", "rec2", "..."]
}
"""
    )
    return "\n".join(lines).strip()


def analyze_budget(req: BudgetAnalysisRequest) -> BudgetAnalysisResponse:
    """
    Call OpenAI to analyze the budget and return validated response.
    Raises ValueError if API key is missing or response is invalid JSON.
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key or not str(api_key).strip():
        raise ValueError("OPENAI_API_KEY is not set")

    model = settings.OPENAI_MODEL or "gpt-4o-mini"

    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(req)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from LLM")

    # Strip markdown code blocks if present
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}") from e

    return BudgetAnalysisResponse(
        narrative=data.get("narrative", ""),
        risks=data.get("risks", []) if isinstance(data.get("risks"), list) else [],
        recommendations=(
            data.get("recommendations", [])
            if isinstance(data.get("recommendations"), list)
            else []
        ),
    )
