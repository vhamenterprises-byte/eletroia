"""Deterministic stub provider — used in tests and local dev without an API key."""

from app.ai.provider import AIProvider, ChatMessage


class MockAIProvider(AIProvider):
    def complete(
        self, system_prompt: str, messages: list[ChatMessage], max_tokens: int = 1024
    ) -> str:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return f"[mock-ai] recebi: {last_user[:200]}"
