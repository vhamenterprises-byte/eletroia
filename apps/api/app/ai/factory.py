from functools import lru_cache

from app.ai.provider import AIProvider
from app.core.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider == "claude" and settings.anthropic_api_key:
        from app.ai.claude_provider import ClaudeAIProvider

        return ClaudeAIProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)

    from app.ai.mock_provider import MockAIProvider

    return MockAIProvider()
