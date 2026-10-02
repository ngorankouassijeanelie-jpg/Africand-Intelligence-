import json
import logging

import httpx

from app.modules.ai.base import AIProvider, ExtractionContext, ExtractionResult
from app.modules.ai.providers.mock_provider import MockAIProvider
from app.modules.ai.providers.prompt import build_extraction_prompt

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self._fallback = MockAIProvider()

    def extract(self, text: str, title: str, context: ExtractionContext) -> ExtractionResult:
        prompt = build_extraction_prompt(text, title, context)
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0,
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return ExtractionResult(**data)
        except Exception:
            logger.exception("Echec extraction OpenAI, repli sur le moteur par mots-cles")
            return self._fallback.extract(text, title, context)
