import json
import logging

from openai import OpenAI, OpenAIError

from app.config import settings
from app.models.task import AIAnalysisResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an operations assistant. Analyse the task provided and respond ONLY
with a JSON object (no markdown, no explanation) matching this exact schema:
{
  "category": "<short category label, e.g. DOCUMENT_REQUEST>",
  "priority": "<LOW | MEDIUM | HIGH>",
  "summary": "<one sentence summary>",
  "recommendedAction": "<one sentence recommended action>"
}"""


def analyse_task(title: str, description: str) -> AIAnalysisResult:
    """
    Call the configured OpenRouter model to analyse a task and return a structured result.
    Raises RuntimeError if the API call fails or returns unexpected output.
    """
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )

    user_message = f"Title: {title}\nDescription: {description}"

    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=300,
        )
    except OpenAIError as exc:
        logger.error("OpenAI API error: %s", exc)
        raise RuntimeError(f"AI service error: {exc}") from exc

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
        return AIAnalysisResult(**data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.error("Failed to parse AI response: %s", raw)
        raise RuntimeError(f"AI returned an unexpected format: {raw}") from exc
