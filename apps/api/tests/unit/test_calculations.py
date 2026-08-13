import math

import pytest

from app.engineering.calculations.electrical import (
    apparent_power_va,
    current_single_phase_a,
    current_three_phase_a,
    demand_power_w,
    voltage_drop_pct,
)
from app.engineering.calculations.sizing import select_breaker, select_conductor


def test_current_single_phase_shower_5500w_220v():
    # Chuveiro elétrico clássico: 5500 W / 220 V, fator de potência ~1 (carga resistiva)
    result = current_single_phase_a(active_power_w=5500, voltage_v=220, power_factor=1.0)
    assert result.unit == "A"
    assert math.isclose(result.result, 25.0, rel_tol=1e-6)


def test_current_three_phase():
    result = current_three_phase_a(active_power_w=6000, voltage_v=220, power_factor=1.0)
    expected = 6000 / (math.sqrt(3) * 220)
    assert math.isclose(result.result, expected, rel_tol=1e-9)


def test_apparent_power_requires_valid_power_factor():
    with pytest.raises(ValueError):
        apparent_power_va(active_power_w=1000, power_factor=0)
    with pytest.raises(ValueError):
        apparent_power_va(active_power_w=1000, power_factor=1.5)


def test_demand_power_sums_weighted_loads():
    result = demand_power_w(
        installed_loads_w=[1000, 2000, 5500], demand_factors=[1.0, 0.8, 1.0]
    )
    assert result.result == 1000 * 1.0 + 2000 * 0.8 + 5500 * 1.0


def test_demand_power_requires_matching_lengths():
    with pytest.raises(ValueError):
        demand_power_w(installed_loads_w=[1000, 2000], demand_factors=[1.0])


def test_voltage_drop_short_circuit_no_review_needed():
    result = voltage_drop_pct(
        current_a=25.0, length_m=10, cross_section_mm2=6.0, voltage_v=220, phase="single"
    )
    assert result.result > 0
    assert result.needs_professional_review is False


def test_voltage_drop_long_circuit_flags_review():
    result = voltage_drop_pct(
        current_a=25.0, length_m=45, cross_section_mm2=6.0, voltage_v=220, phase="single"
    )
    assert result.needs_professional_review is True


def test_select_conductor_shower_circuit():
    # Chuveiro 5500W/220V -> ~25A; deve escolher condutor com ampacidade >= 25A
    result = select_conductor(design_current_a=25.0, circuit_type="power")
    assert result.result >= 2.5
    assert result.needs_professional_review is True


def test_select_conductor_respects_lighting_minimum():
    result = select_conductor(design_current_a=1.0, circuit_type="lighting")
    assert result.result == 1.5  # mínimo de iluminação, mesmo com corrente baixíssima


def test_select_conductor_respects_power_minimum():
    result = select_conductor(design_current_a=1.0, circuit_type="power")
    assert result.result == 2.5  # mínimo de tomadas/TUG


def test_select_conductor_exceeding_table_raises():
    with pytest.raises(ValueError):
        select_conductor(design_current_a=99999, circuit_type="power")


def test_select_breaker_coordinates_with_conductor():
    result = select_breaker(design_current_a=25.0, conductor_ampacity_a=36.0)
    assert 25.0 <= result.result <= 36.0


def test_select_breaker_no_valid_option_raises():
    with pytest.raises(ValueError):
        select_breaker(design_current_a=50.0, conductor_ampacity_a=21.0)
