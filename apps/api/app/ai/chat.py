"""Chat contextual do projeto (seção 23 do prompt mestre) — RAG simplificado: a única
fonte de fatos técnicos é o `TraceableExplanation` montado a partir de Rules/Calculations
reais do projeto, nunca a memória do modelo."""

from app.ai.explain import TraceableExplanation
from app.ai.provider import AIProvider, ChatMessage
from app.ai.safety import SYSTEM_PROMPT_GUARDRAILS, check_user_message

CHAT_SYSTEM_PROMPT_TEMPLATE = SYSTEM_PROMPT_GUARDRAILS + """
Você está respondendo perguntas sobre um projeto elétrico específico. Use APENAS os fatos
abaixo — não invente nenhum outro dado técnico:

--- Cálculos disponíveis e resultados de regras deste projeto ---
{facts}
--- fim dos fatos ---
"""


def answer_project_question(
    provider: AIProvider, user_message: str, facts: TraceableExplanation
) -> str:
    safety = check_user_message(user_message)
    if safety.is_unsafe:
        return safety.refusal_message

    system_prompt = CHAT_SYSTEM_PROMPT_TEMPLATE.format(facts=facts.summary)
    return provider.complete(system_prompt, [ChatMessage(role="user", content=user_message)])
