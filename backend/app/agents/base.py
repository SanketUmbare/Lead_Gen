"""
Base AI agent with retry logic.

WHY: OpenAI API calls fail ~1-3% of the time (rate limits, timeouts).
tenacity gives exponential backoff retries — critical for background jobs
where a single failure shouldn't lose a lead forever.

COST: Each agent call costs $0.001-0.05 depending on model/tokens.
At 1000 leads/day with 5 agent calls each = ~$25-250/day in API costs.
Monitor token usage per lead — it's your biggest variable cost.
"""

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx
from bs4 import BeautifulSoup
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    def _call_llm(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = response.choices[0].message.content or "{}"
        logger.info(
            "llm_call_completed",
            agent=self.__class__.__name__,
            tokens=response.usage.total_tokens if response.usage else 0,
        )
        return json.loads(content)

    def _fetch_website_text(self, url: str, max_chars: int = 8000) -> str:
        if not url:
            return ""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                resp = client.get(url, headers={"User-Agent": "LeadGenBot/1.0"})
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                text = soup.get_text(separator=" ", strip=True)
                return text[:max_chars]
        except Exception as e:
            logger.warning("website_fetch_failed", url=url, error=str(e))
            return ""

    @abstractmethod
    def run(self, **kwargs) -> dict[str, Any]:
        ...
