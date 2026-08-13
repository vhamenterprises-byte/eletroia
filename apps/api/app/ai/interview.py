"""Entrevista conduzida pela IA, uma pergunta por vez (seção 10 do prompt mestre)."""

from app.ai.provider import AIProvider, ChatMessage
from app.ai.safety import SYSTEM_PROMPT_GUARDRAILS, check_user_message

INTERVIEW_SYSTEM_PROMPT = SYSTEM_PROMPT_GUARDRAILS + """
Você está conduzindo a entrevista inicial de um projeto elétrico residencial com um
usuário leigo. Regras da entrevista:
- Faça APENAS UMA pergunta por vez, em português simples, sem jargão técnico
  (nunca pergunte "corrente nominal" — pergunte sobre o equipamento que a pessoa quer usar).
- Adapte a próxima pergunta com base nas respostas já dadas (fornecidas abaixo em
  "Estado atual do projeto").
- Não assuma potências de equipamentos — se o usuário não souber, ofereça perguntar o
  modelo ou usar uma estimativa marcada claramente como estimativa.
"""


def ask_next_question(
    provider: AIProvider, project_state_summary: str, last_user_answer: str | None = None
) -> str:
    messages = [
        ChatMessage(
            role="user",
            content=f"Estado atual do projeto:\n{project_state_summary}\n\n"
            + (f"Última resposta do usuário: {last_user_answer}\n\n" if last_user_answer else "")
            + "Qual é a próxima pergunta da entrevista?",
        )
    ]
    return provider.complete(INTERVIEW_SYSTEM_PROMPT, messages, max_tokens=300)


def guard_user_answer(user_answer: str) -> str | None:
    """Returns a refusal message if the answer attempts to force an unsafe shortcut,
    otherwise None (safe to proceed)."""
    check = check_user_message(user_answer)
    return check.refusal_message if check.is_unsafe else None
