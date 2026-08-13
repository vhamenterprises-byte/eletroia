"""Rules Engine — camada 3 (normas) do prompt mestre.

Regras NÃO vivem em prompts de LLM. Cada regra é uma função Python pura, com metadados
rastreáveis (id, norma, versão, severidade) e uma função `evaluate(context)` determinística
que devolve um veredito estruturado. A IA (app.ai) pode explicar o resultado de uma regra
em linguagem natural, mas nunca decide o veredito.

Níveis de severidade (nunca "aprovado pela ABNT" — ver docs/ai-safety.md):
  VERDE    — verificado automaticamente, dentro dos critérios configurados.
  AMARELO  — informação insuficiente ou pendência a confirmar.
  VERMELHO — inconsistência ou risco identificado pelas regras configuradas.
  AZUL     — requer avaliação de profissional habilitado.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

Severity = str  # "VERDE" | "AMARELO" | "VERMELHO" | "AZUL"


@dataclass
class RuleEvaluation:
    rule_code: str
    status: Severity
    message: str
    subject_type: str
    subject_id: str | None = None
    details: dict[str, Any] | None = None


@dataclass
class ElectricalRule:
    rule_code: str
    standard: str
    version: str
    category: str
    title: str
    default_severity: Severity
    applies_when: Callable[[dict[str, Any]], bool]
    evaluate_fn: Callable[[dict[str, Any]], RuleEvaluation]

    def applies(self, context: dict[str, Any]) -> bool:
        return self.applies_when(context)

    def evaluate(self, context: dict[str, Any]) -> RuleEvaluation:
        return self.evaluate_fn(context)


class RulesEngine:
    def __init__(self, rules: list[ElectricalRule]):
        self._rules = rules

    @property
    def rules(self) -> list[ElectricalRule]:
        return list(self._rules)

    def evaluate_all(self, context: dict[str, Any]) -> list[RuleEvaluation]:
        results: list[RuleEvaluation] = []
        for rule in self._rules:
            if rule.applies(context):
                results.append(rule.evaluate(context))
        return results

    def evaluate_one(self, rule_code: str, context: dict[str, Any]) -> RuleEvaluation | None:
        for rule in self._rules:
            if rule.rule_code == rule_code:
                return rule.evaluate(context)
        return None
