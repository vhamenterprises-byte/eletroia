"""Orquestra a geração automática (modo automático — seção 18) de circuitos, quadro e
dimensionamento a partir das cargas cadastradas. Toda decisão passa pelos módulos
determinísticos de cálculo/regras — esta função apenas conecta os dados do projeto a eles.
"""

from sqlalchemy.orm import Session

from app.engineering.calculations.electrical import (
    CalculationResult,
    current_single_phase_a,
    current_three_phase_a,
    voltage_drop_pct,
)
from app.engineering.calculations.sizing import select_breaker, select_conductor
from app.engineering.rules.engine import RuleEvaluation, RulesEngine
from app.engineering.rules.nbr5410 import NBR5410_RULES
from app.engineering.standards.ampacity_table import AMPACITY_TABLE_A
from app.models.electrical import Breaker, Circuit, Conductor, Panel, ProtectionDevice
from app.models.engineering import Calculation, RuleResult
from app.models.project import Project, Room

DEFAULT_LIGHTING_ALLOWANCE_W = 100.0
LIGHTING_POWER_PER_POINT_W = 60.0
GENERAL_OUTLET_POWER_ESTIMATE_W = 100.0
DEFAULT_CIRCUIT_LENGTH_M = 15.0
DEDICATED_THRESHOLD_W = 1500

rules_engine = RulesEngine(NBR5410_RULES)


def _persist_calculation(
    db: Session, project_id, circuit_id, calc: CalculationResult
) -> Calculation:
    row = Calculation(
        project_id=project_id,
        circuit_id=circuit_id,
        calc_type=calc.calc_type,
        formula=calc.formula,
        inputs=calc.inputs,
        result=calc.result,
        unit=calc.unit,
        source=calc.source,
    )
    db.add(row)
    return row


def _persist_rule_result(db: Session, project_id, evaluation: RuleEvaluation) -> RuleResult:
    row = RuleResult(
        project_id=project_id,
        rule_code=evaluation.rule_code,
        subject_type=evaluation.subject_type,
        subject_id=evaluation.subject_id,
        status=evaluation.status,
        message=evaluation.message,
        details=evaluation.details or {},
    )
    db.add(row)
    return row


def _size_circuit(db: Session, project: Project, circuit: Circuit, total_power_w: float) -> None:
    if circuit.phase == "three":
        current_calc = current_three_phase_a(total_power_w, circuit.voltage_v)
    else:
        current_calc = current_single_phase_a(total_power_w, circuit.voltage_v)
    _persist_calculation(db, project.id, circuit.id, current_calc)

    conductor_calc = select_conductor(
        design_current_a=current_calc.result, circuit_type=circuit.circuit_type
    )
    _persist_calculation(db, project.id, circuit.id, conductor_calc)

    installation_method = conductor_calc.inputs["installation_method"]
    ampacity_a = AMPACITY_TABLE_A[installation_method][conductor_calc.result]

    breaker_calc = select_breaker(
        design_current_a=current_calc.result, conductor_ampacity_a=ampacity_a
    )
    _persist_calculation(db, project.id, circuit.id, breaker_calc)

    vdrop_calc = voltage_drop_pct(
        current_a=current_calc.result,
        length_m=DEFAULT_CIRCUIT_LENGTH_M,
        cross_section_mm2=conductor_calc.result,
        voltage_v=circuit.voltage_v,
        phase=circuit.phase,
    )
    _persist_calculation(db, project.id, circuit.id, vdrop_calc)

    db.add(
        Conductor(
            circuit_id=circuit.id,
            cross_section_mm2=conductor_calc.result,
            installation_method="B1_conduit_wall",
            ampacity_a=ampacity_a,
            voltage_drop_pct=vdrop_calc.result,
        )
    )
    db.add(Breaker(circuit_id=circuit.id, rated_current_a=breaker_calc.result, curve="C", poles=1))

    rule_ctx = {
        "circuit": {"id": circuit.id, "name": circuit.name, "circuit_type": circuit.circuit_type},
        "conductor": {"cross_section_mm2": conductor_calc.result},
    }
    for evaluation in rules_engine.evaluate_all(rule_ctx):
        _persist_rule_result(db, project.id, evaluation)


def generate_electrical_design(db: Session, project: Project) -> dict:
    """Regenerates circuits/panel/conductors/breakers/rule results for a project from its
    current rooms and loads. Idempotent: clears previously generated circuits/panel."""

    rooms: list[Room] = project.rooms

    for room in rooms:
        for load in room.loads:
            load.circuit_id = None

    old_circuits = db.query(Circuit).filter(Circuit.project_id == project.id).all()
    for c in old_circuits:
        db.delete(c)
    old_panels = db.query(Panel).filter(Panel.project_id == project.id).all()
    for p in old_panels:
        db.delete(p)
    db.query(RuleResult).filter(RuleResult.project_id == project.id).delete()
    db.query(Calculation).filter(Calculation.project_id == project.id).delete()
    db.flush()

    panel = Panel(project_id=project.id, name="QDC-01")
    db.add(panel)
    db.add(ProtectionDevice(panel=panel, device_type="DR", sensitivity_ma=30, rated_current_a=40))
    db.add(ProtectionDevice(panel=panel, device_type="DPS", notes="Classe II"))
    db.flush()

    created_circuits: list[Circuit] = []

    for room in rooms:
        light_points = room.light_point_count
        room_has_lighting = light_points is None or light_points > 0
        lighting_power = (
            light_points * LIGHTING_POWER_PER_POINT_W
            if light_points
            else DEFAULT_LIGHTING_ALLOWANCE_W
        )

        lighting_circuit = Circuit(
            project_id=project.id,
            panel_id=panel.id,
            name=f"Iluminação {room.name}",
            circuit_type="lighting",
            voltage_v=127,
            phase="single",
        )
        db.add(lighting_circuit)
        db.flush()
        _size_circuit(db, project, lighting_circuit, lighting_power)
        created_circuits.append(lighting_circuit)

        rule_ctx = {
            "room": {"id": room.id, "name": room.name},
            "room_has_lighting": room_has_lighting,
        }
        for evaluation in rules_engine.evaluate_all(rule_ctx):
            _persist_rule_result(db, project.id, evaluation)

        outlet_count = room.outlet_count or 0
        general_loads = [ld for ld in room.loads if ld.nominal_power_w < DEDICATED_THRESHOLD_W]
        if general_loads or outlet_count > 0:
            tug_circuit = Circuit(
                project_id=project.id,
                panel_id=panel.id,
                name=f"TUG {room.name}",
                circuit_type="power",
                voltage_v=127,
                phase="single",
            )
            db.add(tug_circuit)
            db.flush()
            for ld in general_loads:
                ld.circuit_id = tug_circuit.id
            total = sum(ld.nominal_power_w for ld in general_loads)
            total += outlet_count * GENERAL_OUTLET_POWER_ESTIMATE_W
            _size_circuit(db, project, tug_circuit, total)
            created_circuits.append(tug_circuit)

            if room.perimeter_m is not None:
                tug_ctx = {
                    "room": {
                        "id": room.id,
                        "name": room.name,
                        "perimeter_m": room.perimeter_m,
                        "room_type": room.room_type,
                    },
                    "tug_count": outlet_count,
                }
                for evaluation in rules_engine.evaluate_all(tug_ctx):
                    _persist_rule_result(db, project.id, evaluation)

        dedicated_loads = [ld for ld in room.loads if ld.nominal_power_w >= DEDICATED_THRESHOLD_W]
        for ld in dedicated_loads:
            ld.requires_dedicated_circuit = True
            dedicated_circuit = Circuit(
                project_id=project.id,
                panel_id=panel.id,
                name=f"{ld.name} ({room.name})",
                circuit_type="dedicated",
                voltage_v=ld.voltage_v,
                phase="single",
            )
            db.add(dedicated_circuit)
            db.flush()
            ld.circuit_id = dedicated_circuit.id
            _size_circuit(db, project, dedicated_circuit, ld.nominal_power_w)
            created_circuits.append(dedicated_circuit)

            rule_ctx = {
                "load": {
                    "id": ld.id,
                    "name": ld.name,
                    "nominal_power_w": ld.nominal_power_w,
                    "requires_dedicated_circuit": True,
                    "circuit_id": dedicated_circuit.id,
                }
            }
            for evaluation in rules_engine.evaluate_all(rule_ctx):
                _persist_rule_result(db, project.id, evaluation)

    panel_ctx = {
        "panel": {"id": panel.id, "name": panel.name},
        "protection_devices": [{"device_type": "DR"}, {"device_type": "DPS"}],
        "check_grounding": True,
    }
    for evaluation in rules_engine.evaluate_all(panel_ctx):
        _persist_rule_result(db, project.id, evaluation)

    db.commit()
    return {"panel_id": str(panel.id), "circuit_count": len(created_circuits)}
