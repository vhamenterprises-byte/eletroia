"""Monta explicações rastreáveis: toda resposta técnica aponta para a regra/cálculo que a
sustenta (seção 24/44 do prompt mestre)."""

from dataclasses import dataclass

from app.engineering.calculations.electrical import CalculationResult
from app.engineering.rules.engine import RuleEvaluation


@dataclass
class TraceableExplanation:
    summary: str
    rule_codes: list[str]
    calculation_types: list[str]
    raw_rules: list[RuleEvaluation]
    raw_calculations: list[CalculationResult]


def build_explanation(
    rules: list[RuleEvaluation], calculations: list[CalculationResult]
) -> TraceableExplanation:
    lines = []
    for r in rules:
        lines.append(f"[{r.status}] {r.rule_code}: {r.message}")
    for c in calculations:
        review = " (requer revisão profissional)" if c.needs_professional_review else ""
        lines.append(f"[CALC] {c.calc_type} = {c.result} {c.unit} — fórmula: {c.formula}{review}")

    return TraceableExplanation(
        summary="\n".join(lines) if lines else "Nenhuma regra ou cálculo aplicável encontrado.",
        rule_codes=[r.rule_code for r in rules],
        calculation_types=[c.calc_type for c in calculations],
        raw_rules=rules,
        raw_calculations=calculations,
    )
