"""Conductor and breaker selection — deterministic, table-driven (never LLM-driven)."""

from app.engineering.calculations.electrical import CalculationResult
from app.engineering.standards.ampacity_table import (
    AMPACITY_TABLE_A,
    MIN_CROSS_SECTION_LIGHTING_MM2,
    MIN_CROSS_SECTION_POWER_MM2,
    STANDARD_BREAKER_RATINGS_A,
)


def select_conductor(
    design_current_a: float,
    installation_method: str = "B1_conduit_wall",
    circuit_type: str = "power",
) -> CalculationResult:
    """Picks the smallest standard cross-section whose ampacity >= design current, honoring
    the minimum cross-section required for the circuit type (lighting vs power/tomadas)."""
    table = AMPACITY_TABLE_A.get(installation_method)
    if table is None:
        raise ValueError(f"Método de instalação desconhecido: {installation_method}")

    min_section = (
        MIN_CROSS_SECTION_LIGHTING_MM2
        if circuit_type == "lighting"
        else MIN_CROSS_SECTION_POWER_MM2
    )

    chosen_section: float | None = None
    chosen_ampacity: float | None = None
    for section, ampacity in sorted(table.items()):
        if section < min_section:
            continue
        if ampacity >= design_current_a:
            chosen_section, chosen_ampacity = section, ampacity
            break

    if chosen_section is None:
        largest_section = max(table)
        raise ValueError(
            f"Corrente de projeto ({design_current_a:.1f} A) excede a maior seção "
            f"disponível na tabela ({largest_section} mm² -> {table[largest_section]} A). "
            "Requer avaliação profissional (múltiplos condutores em paralelo ou outro "
            "método de instalação)."
        )

    return CalculationResult(
        calc_type="conductor_selection",
        formula="menor secao padrao cuja ampacidade tabelada >= corrente de projeto",
        inputs={
            "design_current_a": design_current_a,
            "installation_method": installation_method,
            "circuit_type": circuit_type,
            "min_cross_section_mm2": min_section,
        },
        result=chosen_section,
        unit="mm2",
        needs_professional_review=True,
        notes=(
            f"Ampacidade tabelada: {chosen_ampacity} A (tabela interna simplificada — "
            "requer validação por profissional habilitado antes de execução)."
        ),
    )


def select_breaker(design_current_a: float, conductor_ampacity_a: float) -> CalculationResult:
    """Picks the smallest standard breaker rating that is >= design current and
    <= conductor ampacity (protects the conductor, per the general coordination
    principle I_design <= I_breaker <= I_conductor)."""
    candidates = [
        r for r in STANDARD_BREAKER_RATINGS_A if r >= design_current_a and r <= conductor_ampacity_a
    ]
    if not candidates:
        raise ValueError(
            f"Nenhum disjuntor padrão coordena corrente de projeto ({design_current_a:.1f} A) "
            f"com a ampacidade do condutor ({conductor_ampacity_a} A). Requer avaliação "
            "profissional."
        )
    chosen = min(candidates)
    return CalculationResult(
        calc_type="breaker_selection",
        formula="menor In padrao tal que I_projeto <= In <= I_condutor",
        inputs={
            "design_current_a": design_current_a,
            "conductor_ampacity_a": conductor_ampacity_a,
        },
        result=chosen,
        unit="A",
        needs_professional_review=True,
        notes="Seleção de disjuntor por coordenação corrente-ampacidade; validar curva (B/C/D) conforme carga.",
    )
