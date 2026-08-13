"""AIProvider — camada 4 (IA) do prompt mestre, independente de fornecedor.

Nada nesta camada decide um cálculo elétrico ou um veredito normativo: `complete()`
apenas gera texto em linguagem natural a partir de um prompt de sistema e uma lista de
mensagens. Todo fato técnico citado no prompt de sistema deve vir de
`app.engineering.calculations` / `app.engineering.rules` — nunca do próprio modelo.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str


class AIProvider(ABC):
    @abstractmethod
    def complete(
        self, system_prompt: str, messages: list[ChatMessage], max_tokens: int = 1024
    ) -> str:
        """Returns the assistant's natural-language reply. Never call this to obtain a
        number or a compliance verdict — those come from the engineering/rules layers."""
        raise NotImplementedError
