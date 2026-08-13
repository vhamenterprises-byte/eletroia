from app.engineering.rules.engine import RulesEngine
from app.engineering.rules.nbr5410 import NBR5410_RULES

engine = RulesEngine(NBR5410_RULES)


def test_room_without_lighting_is_red():
    context = {"room": {"id": "r1", "name": "Sala"}, "room_has_lighting": False}
    result = engine.evaluate_one("RULE-LIGHTING-MIN-CIRCUIT", context)
    assert result.status == "VERMELHO"


def test_room_with_lighting_is_green():
    context = {"room": {"id": "r1", "name": "Sala"}, "room_has_lighting": True}
    result = engine.evaluate_one("RULE-LIGHTING-MIN-CIRCUIT", context)
    assert result.status == "VERDE"


def test_tug_count_below_minimum_is_yellow():
    context = {
        "room": {"id": "r1", "name": "Sala", "perimeter_m": 20, "room_type": "sala"},
        "tug_count": 1,
    }
    result = engine.evaluate_one("RULE-TUG-MIN-COUNT", context)
    assert result.status == "AMARELO"
    assert result.details["min_required"] == 4


def test_tug_count_meets_minimum_is_green():
    context = {
        "room": {"id": "r1", "name": "Sala", "perimeter_m": 20, "room_type": "sala"},
        "tug_count": 4,
    }
    result = engine.evaluate_one("RULE-TUG-MIN-COUNT", context)
    assert result.status == "VERDE"


def test_high_power_load_without_dedicated_circuit_is_red():
    context = {
        "load": {
            "id": "l1",
            "name": "Chuveiro",
            "nominal_power_w": 5500,
            "requires_dedicated_circuit": True,
            "circuit_id": None,
        }
    }
    result = engine.evaluate_one("RULE-DEDICATED-CIRCUIT-HIGH-POWER", context)
    assert result.status == "VERMELHO"


def test_high_power_load_with_dedicated_circuit_is_green():
    context = {
        "load": {
            "id": "l1",
            "name": "Chuveiro",
            "nominal_power_w": 5500,
            "requires_dedicated_circuit": True,
            "circuit_id": "c1",
        }
    }
    result = engine.evaluate_one("RULE-DEDICATED-CIRCUIT-HIGH-POWER", context)
    assert result.status == "VERDE"


def test_low_power_load_does_not_require_dedicated_circuit():
    context = {
        "load": {
            "id": "l1",
            "name": "Abajur",
            "nominal_power_w": 60,
            "requires_dedicated_circuit": False,
            "circuit_id": None,
        }
    }
    result = engine.evaluate_one("RULE-DEDICATED-CIRCUIT-HIGH-POWER", context)
    assert result.status == "VERDE"


def test_socket_inside_shower_box_is_rejected():
    """Caso do prompt mestre (seção 14): tomada dentro do box do chuveiro deve ser
    bloqueada, não aceita silenciosamente."""
    context = {
        "socket_placement_request": {
            "id": "req1",
            "room_type": "banheiro",
            "distance_from_water_source_m": 0.0,
        }
    }
    result = engine.evaluate_one("RULE-WET-AREA-SOCKET-CLEARANCE", context)
    assert result.status == "VERMELHO"


def test_socket_far_from_water_is_accepted():
    context = {
        "socket_placement_request": {
            "id": "req1",
            "room_type": "banheiro",
            "distance_from_water_source_m": 1.2,
        }
    }
    result = engine.evaluate_one("RULE-WET-AREA-SOCKET-CLEARANCE", context)
    assert result.status == "VERDE"


def test_conductor_below_minimum_section_is_red():
    context = {
        "circuit": {"id": "c1", "name": "TUG Cozinha", "circuit_type": "power"},
        "conductor": {"cross_section_mm2": 1.5},
    }
    result = engine.evaluate_one("RULE-MIN-CONDUCTOR-SECTION", context)
    assert result.status == "VERMELHO"


def test_panel_without_dr_is_red():
    context = {
        "panel": {"id": "p1", "name": "QDC-01"},
        "protection_devices": [{"device_type": "DPS"}],
    }
    result = engine.evaluate_one("RULE-DR-PROTECTION-REQUIRED", context)
    assert result.status == "VERMELHO"


def test_panel_with_dr_is_green():
    context = {
        "panel": {"id": "p1", "name": "QDC-01"},
        "protection_devices": [{"device_type": "DR"}],
    }
    result = engine.evaluate_one("RULE-DR-PROTECTION-REQUIRED", context)
    assert result.status == "VERDE"


def test_grounding_always_needs_professional_review():
    context = {"panel": {"id": "p1", "name": "QDC-01"}, "check_grounding": True}
    result = engine.evaluate_one("RULE-GROUNDING-REVIEW", context)
    assert result.status == "AZUL"


def test_evaluate_all_only_runs_applicable_rules():
    context = {"room": {"id": "r1", "name": "Sala"}, "room_has_lighting": True}
    results = engine.evaluate_all(context)
    codes = {r.rule_code for r in results}
    assert codes == {"RULE-LIGHTING-MIN-CIRCUIT"}
