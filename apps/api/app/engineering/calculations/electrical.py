"""Deterministic electrical calculation engine.

Every public function here is a pure function: given the same inputs, it always returns
the same result. No LLM call may ever substitute for a function in this module — the AI
layer (app.ai) can only *call* these functions and *explain* their results, never invent
a number that should have come from here.

Each function returns a `CalculationResult`, which is what gets persisted to the
`calculations` table for auditability (input/formula/parameters/result/unit/source).
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SQRT3 = math.sqrt(3)

# Copper resistivity (ohm.mm2/m) at ~70C, used for a simplified voltage-drop estimate.
COPPER_RESISTIVITY_OHM_MM2_PER_M = 0.0225


@dataclass
class CalculationResult:
    calc_type: str
    formula: str
    inputs: dict[str, Any]
    result: float
    unit: str
    source: str = "app.engineering.calculations.electrical"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    needs_professional_review: bool = False
    notes: str | None = None


def apparent_power_va(active_power_w: float, power_factor: float) -> CalculationResult:
    """S (VA) = P (W) / cos(phi)"""
    if not 0 < power_factor <= 1:
        raise ValueError("power_factor deve estar entre 0 (exclusivo) e 1")
    result = active_power_w / power_factor
    return CalculationResult(
        calc_type="apparent_power",
        formula="S = P / cos(phi)",
        inputs={"active_power_w": active_power_w, "power_factor": power_factor},
        result=result,
        unit="VA",
    )


def current_single_phase_a(
    active_power_w: float, voltage_v: float, power_factor: float = 1.0
) -> CalculationResult:
    """I (A) = P (W) / (V (V) * cos(phi)) — circuito monofásico ou fase-neutro."""
    if voltage_v <= 0:
        raise ValueError("voltage_v deve ser positivo")
    result = active_power_w / (voltage_v * power_factor)
    return CalculationResult(
        calc_type="current_single_phase",
        formula="I = P / (V * cos(phi))",
        inputs={
            "active_power_w": active_power_w,
            "voltage_v": voltage_v,
            "power_factor": power_factor,
        },
        result=result,
        unit="A",
    )


def current_three_phase_a(
    active_power_w: float, voltage_v: float, power_factor: float = 1.0
) -> CalculationResult:
    """I (A) = P (W) / (sqrt(3) * V (V) * cos(phi)) — circuito trifásico (tensão de linha)."""
    if voltage_v <= 0:
        raise ValueError("voltage_v deve ser positivo")
    result = active_power_w / (SQRT3 * voltage_v * power_factor)
    return CalculationResult(
        calc_type="current_three_phase",
        formula="I = P / (sqrt(3) * V * cos(phi))",
        inputs={
            "active_power_w": active_power_w,
            "voltage_v": voltage_v,
            "power_factor": power_factor,
        },
        result=result,
        unit="A",
    )


def demand_power_w(
    installed_loads_w: list[float], demand_factors: list[float]
) -> CalculationResult:
    """Potência demandada = soma(potência instalada_i * fator de demanda_i).

    `demand_factors` deve ter o mesmo tamanho de `installed_loads_w` — cada carga tem seu
    próprio fator de demanda (nunca aplique um fator único "de cabeça" para a residência
    inteira sem justificar por carga).
    """
    if len(installed_loads_w) != len(demand_factors):
        raise ValueError("installed_loads_w e demand_factors devem ter o mesmo tamanho")
    result = sum(p * f for p, f in zip(installed_loads_w, demand_factors, strict=True))
    return CalculationResult(
        calc_type="demand_power",
        formula="P_demandada = sum(P_instalada_i * FD_i)",
        inputs={"installed_loads_w": installed_loads_w, "demand_factors": demand_factors},
        result=result,
        unit="W",
    )


def voltage_drop_pct(
    current_a: float,
    length_m: float,
    cross_section_mm2: float,
    voltage_v: float,
    phase: str = "single",
) -> CalculationResult:
    """Queda de tensão percentual estimada por resistência do condutor (sem reatância).

    Delta_V = 2 * rho * L * I / S   (monofásico, ida e volta)
    Delta_V = sqrt(3) * rho * L * I / S   (trifásico)

    Esta é uma estimativa simplificada baseada apenas em resistência (adequada para baixa
    tensão / condutores de pequena seção em corrente contínua/baixa frequência). Circuitos
    de grande porte ou grande comprimento devem ser revisados considerando reatância —
    sinalizado via `needs_professional_review`.
    """
    if cross_section_mm2 <= 0 or voltage_v <= 0:
        raise ValueError("cross_section_mm2 e voltage_v devem ser positivos")

    factor = 2 if phase == "single" else SQRT3
    delta_v = factor * COPPER_RESISTIVITY_OHM_MM2_PER_M * length_m * current_a / cross_section_mm2
    pct = (delta_v / voltage_v) * 100

    return CalculationResult(
        calc_type="voltage_drop",
        formula="dV%% = (factor * rho * L * I / S) / V * 100",
        inputs={
            "current_a": current_a,
            "length_m": length_m,
            "cross_section_mm2": cross_section_mm2,
            "voltage_v": voltage_v,
            "phase": phase,
        },
        result=round(pct, 3),
        unit="%",
        needs_professional_review=length_m > 30,
        notes=(
            "Estimativa baseada apenas em resistência do condutor; circuitos longos "
            "(>30m) devem ser revisados por profissional considerando reatância."
            if length_m > 30
            else None
        ),
    )
