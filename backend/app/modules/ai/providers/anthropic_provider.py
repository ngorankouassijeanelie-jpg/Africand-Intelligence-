import json
import logging

import httpx

from app.modules.ai.base import AIProvider, ExtractionContext, ExtractionResult
from app.modules.ai.providers.mock_provider import MockAIProvider
from app.modules.ai.providers.prompt import build_extraction_prompt

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-sonnet-5-5"):
        self.api_key = api_key
        self.model = model
        self._fallback = MockAIProvider()

    def extract(self, text: str, title: str, context: ExtractionContext) -> ExtractionResult:
        prompt = build_extraction_prompt(text, title, context)
        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["content"][0]["text"]
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            data = json.loads(content[json_start:json_end])
            return ExtractionResult(**data)
        except Exception:
            logger.exception("Echec extraction Anthropic, repli sur le moteur par mots-cles")
            return self._fallback.extract(text, title, context)
