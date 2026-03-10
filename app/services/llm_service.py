"""LLM service for budget analysis using Google Gemini."""
import json
import re

import google.generativeai as genai

from app.config import settings
from app.schemas.budget_analysis import BudgetAnalysisRequest, BudgetAnalysisResponse


def _build_prompt(req: BudgetAnalysisRequest) -> str:
    """Build a structured prompt for an expert film production budget analyst."""
    lines = [
        "You are an expert film production budget analyst. Analyze this budget and provide a professional assessment.",
        "",
        "## Budget summary",
    ]
    total = sum(c.amount for c in req.categories)
    for cat in req.categories:
        lines.append(
            f"- {cat.name}: {req.currency or 'USD'} {cat.amount:,.2f} ({cat.percentage:.1f}%)"
        )
    lines.append(f"\nTotal: {req.currency or 'USD'} {total:,.2f}")
    if req.projectType:
        lines.append(f"\nProject type: {req.projectType}")
    if req.location:
        lines.append(f"Location: {req.location}")
    if req.unionStatus:
        lines.append(f"Union status: {req.unionStatus}")
    lines.append(
        """
Respond with ONLY valid JSON, no markdown, no code fences, no extra text. Use this exact structure:
{
  "narrative": "A 2-4 sentence analysis of the budget structure and appropriateness.",
  "risks": ["risk1", "risk2", "..."],
  "recommendations": ["rec1", "rec2", "..."]
}
"""
    )
    return "\n".join(lines).strip()


def _extract_text(response) -> str:
    """Extract text from Gemini response safely."""
    if hasattr(response, "text") and response.text:
        return response.text
    if hasattr(response, "candidates") and response.candidates:
        cand = response.candidates[0]
        if hasattr(cand, "content") and cand.content and hasattr(cand.content, "parts"):
            for part in cand.content.parts:
                if hasattr(part, "text") and part.text:
                    return part.text
    return ""


def analyze_budget(req: BudgetAnalysisRequest) -> BudgetAnalysisResponse:
    """
    Call Google Gemini to analyze the budget and return validated response.
    Raises ValueError if API key is missing or response is invalid JSON.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key or not str(api_key).strip():
        raise ValueError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = _build_prompt(req)

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.3),
    )
    content = _extract_text(response)
    if not content or not content.strip():
        raise ValueError("Empty response from LLM")

    # Strip markdown code fences if present
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
