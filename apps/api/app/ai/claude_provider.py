from anthropic import Anthropic

from app.ai.provider import AIProvider, ChatMessage


class ClaudeAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def complete(
        self, system_prompt: str, messages: list[ChatMessage], max_tokens: int = 1024
    ) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return "".join(block.text for block in response.content if block.type == "text")
