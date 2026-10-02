import logging

from app.core.config import get_settings
from app.modules.ai.base import AIProvider, ExtractionContext, ExtractionResult
from app.modules.ai.providers.mock_provider import MockAIProvider

logger = logging.getLogger(__name__)


def get_ai_provider() -> AIProvider:
    """Factory retournant le fournisseur IA configure (AI_PROVIDER dans .env).

    Le moteur est concu pour etre agnostique du fournisseur : changer de LLM
    ne necessite qu'un changement de configuration, jamais de code metier.
    """
    settings = get_settings()
    provider = settings.ai_provider.lower()

    if provider == "openai" and settings.openai_api_key:
        from app.modules.ai.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=settings.openai_api_key)

    if provider == "anthropic" and settings.anthropic_api_key:
        from app.modules.ai.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=settings.anthropic_api_key)

    if provider not in ("mock", ""):
        logger.warning("Fournisseur IA '%s' non configure (cle API manquante), repli sur 'mock'", provider)

    return MockAIProvider()


def extract_opportunity(text: str, title: str, context: ExtractionContext) -> ExtractionResult:
    return get_ai_provider().extract(text, title, context)
