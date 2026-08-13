"""Regras iniciais (subconjunto do MVP) inspiradas em critérios amplamente conhecidos de
instalações elétricas residenciais de baixa tensão no Brasil (NBR 5410).

IMPORTANTE: os limiares numéricos aqui são uma interpretação interna simplificada para o
MVP — não uma transcrição do texto da norma — e devem ser revisados/ajustados por um
profissional habilitado antes de uso em projetos reais (ver `NormativeReference` para o
apontamento estruturado de onde cada regra se origina, sem copiar o texto protegido).
"""

from typing import Any

from app.engineering.rules.engine import ElectricalRule, RuleEvaluation

WET_AREAS = {"banheiro", "area_servico", "cozinha"}
DEDICATED_CIRCUIT_THRESHOLD_W = 1500
MIN_SOCKET_DISTANCE_FROM_WATER_M = 0.60


def _lighting_min_circuit(context: dict[str, Any]) -> RuleEvaluation:
    room = context["room"]
    has_lighting = bool(context.get("room_has_lighting", False))
    status = "VERDE" if has_lighting else "VERMELHO"
    message = (
        f"O ambiente '{room['name']}' possui pelo menos um ponto de iluminação atribuído."
        if has_lighting
        else f"O ambiente '{room['name']}' ainda não possui nenhum ponto de iluminação — todo cômodo precisa de ao menos um."
    )
    return RuleEvaluation(
        rule_code="RULE-LIGHTING-MIN-CIRCUIT",
        status=status,
        message=message,
        subject_type="room",
        subject_id=str(room["id"]),
    )


def _tug_minimum_count(context: dict[str, Any]) -> RuleEvaluation:
    room = context["room"]
    perimeter_m = room.get("perimeter_m")
    tug_count = context.get("tug_count", 0)
    room_type = room.get("room_type", "")

    if perimeter_m is None:
        return RuleEvaluation(
            rule_code="RULE-TUG-MIN-COUNT",
            status="AMARELO",
            message=f"Perímetro do ambiente '{room['name']}' não informado — não é possível calcular o número mínimo de tomadas.",
            subject_type="room",
            subject_id=str(room["id"]),
        )

    spacing = 3.5 if room_type in WET_AREAS else 5.0
    min_required = max(1, math_ceil(perimeter_m / spacing))

    status = "VERDE" if tug_count >= min_required else "AMARELO"
    message = (
        f"O ambiente '{room['name']}' possui {tug_count} tomada(s) de uso geral, "
        f"atendendo ao mínimo estimado de {min_required} para este perímetro."
        if status == "VERDE"
        else f"O ambiente '{room['name']}' possui {tug_count} tomada(s), abaixo do mínimo "
        f"estimado de {min_required} para este perímetro — considere adicionar mais tomadas."
    )
    return RuleEvaluation(
        rule_code="RULE-TUG-MIN-COUNT",
        status=status,
        message=message,
        subject_type="room",
        subject_id=str(room["id"]),
        details={"min_required": min_required, "current_count": tug_count},
    )


def math_ceil(value: float) -> int:
    import math

    return math.ceil(value)


def _dedicated_circuit_high_power(context: dict[str, Any]) -> RuleEvaluation:
    load = context["load"]
    power_w = load["nominal_power_w"]
    on_dedicated = bool(load.get("requires_dedicated_circuit") and load.get("circuit_id"))

    if power_w < DEDICATED_CIRCUIT_THRESHOLD_W:
        status = "VERDE"
        message = f"'{load['name']}' ({power_w:.0f} W) não exige circuito dedicado pelo critério configurado."
    elif on_dedicated:
        status = "VERDE"
        message = f"'{load['name']}' ({power_w:.0f} W) está corretamente em um circuito dedicado."
    else:
        status = "VERMELHO"
        message = (
            f"'{load['name']}' ({power_w:.0f} W) é uma carga de alta potência e precisa de "
            "um circuito dedicado, mas ainda não está associado a um."
        )
    return RuleEvaluation(
        rule_code="RULE-DEDICATED-CIRCUIT-HIGH-POWER",
        status=status,
        message=message,
        subject_type="load",
        subject_id=str(load["id"]),
    )


def _wet_area_socket_clearance(context: dict[str, Any]) -> RuleEvaluation:
    request = context["socket_placement_request"]
    room_type = request.get("room_type", "")
    distance_m = request.get("distance_from_water_source_m")

    if room_type not in WET_AREAS:
        status, message = "VERDE", "Ambiente não classificado como área molhada para esta verificação."
    elif distance_m is None:
        status = "AMARELO"
        message = (
            "Distância da tomada até a fonte de água (chuveiro/torneira) não informada — "
            "não é possível confirmar a segurança do posicionamento."
        )
    elif distance_m < MIN_SOCKET_DISTANCE_FROM_WATER_M:
        status = "VERMELHO"
        message = (
            f"Posicionamento proposto fica a {distance_m:.2f} m da fonte de água, abaixo do "
            f"mínimo de segurança configurado ({MIN_SOCKET_DISTANCE_FROM_WATER_M:.2f} m). "
            "Esta configuração não pode ser aceita automaticamente."
        )
    else:
        status = "VERDE"
        message = f"Posicionamento a {distance_m:.2f} m da fonte de água atende à distância mínima configurada."

    return RuleEvaluation(
        rule_code="RULE-WET-AREA-SOCKET-CLEARANCE",
        status=status,
        message=message,
        subject_type="socket_placement_request",
        subject_id=request.get("id"),
    )


def _min_conductor_section(context: dict[str, Any]) -> RuleEvaluation:
    circuit = context["circuit"]
    conductor = context["conductor"]
    min_section = 1.5 if circuit["circuit_type"] == "lighting" else 2.5
    section = conductor["cross_section_mm2"]
    status = "VERDE" if section >= min_section else "VERMELHO"
    message = (
        f"Condutor do circuito '{circuit['name']}' ({section} mm²) atende à seção mínima "
        f"configurada ({min_section} mm²)."
        if status == "VERDE"
        else f"Condutor do circuito '{circuit['name']}' ({section} mm²) está abaixo da seção "
        f"mínima configurada ({min_section} mm²) para este tipo de circuito."
    )
    return RuleEvaluation(
        rule_code="RULE-MIN-CONDUCTOR-SECTION",
        status=status,
        message=message,
        subject_type="circuit",
        subject_id=str(circuit["id"]),
    )


def _dr_protection_required(context: dict[str, Any]) -> RuleEvaluation:
    panel = context["panel"]
    has_dr = any(d.get("device_type") == "DR" for d in context.get("protection_devices", []))
    status = "VERDE" if has_dr else "VERMELHO"
    message = (
        f"O quadro '{panel['name']}' possui dispositivo DR configurado."
        if has_dr
        else f"O quadro '{panel['name']}' ainda não possui um dispositivo DR (diferencial "
        "residual) configurado — necessário para proteção contra choques elétricos."
    )
    return RuleEvaluation(
        rule_code="RULE-DR-PROTECTION-REQUIRED",
        status=status,
        message=message,
        subject_type="panel",
        subject_id=str(panel["id"]),
    )


def _grounding_professional_review(context: dict[str, Any]) -> RuleEvaluation:
    panel = context["panel"]
    return RuleEvaluation(
        rule_code="RULE-GROUNDING-REVIEW",
        status="AZUL",
        message=(
            "O aterramento e a resistência de terra não podem ser validados remotamente — "
            "este item requer medição e avaliação de um profissional habilitado no local."
        ),
        subject_type="panel",
        subject_id=str(panel["id"]),
    )


NBR5410_RULES: list[ElectricalRule] = [
    ElectricalRule(
        rule_code="RULE-LIGHTING-MIN-CIRCUIT",
        standard="NBR 5410",
        version="MVP-interno-v1",
        category="iluminacao",
        title="Todo ambiente precisa de ao menos um ponto de iluminação",
        default_severity="VERMELHO",
        applies_when=lambda ctx: "room" in ctx and "room_has_lighting" in ctx,
        evaluate_fn=_lighting_min_circuit,
    ),
    ElectricalRule(
        rule_code="RULE-TUG-MIN-COUNT",
        standard="NBR 5410",
        version="MVP-interno-v1",
        category="tomadas",
        title="Número mínimo de tomadas de uso geral por perímetro do ambiente",
        default_severity="AMARELO",
        applies_when=lambda ctx: "room" in ctx and "tug_count" in ctx,
        evaluate_fn=_tug_minimum_count,
    ),
    ElectricalRule(
        rule_code="RULE-DEDICATED-CIRCUIT-HIGH-POWER",
        standard="NBR 5410",
        version="MVP-interno-v1",
        category="circuitos",
        title="Cargas de alta potência exigem circuito dedicado",
        default_severity="VERMELHO",
        applies_when=lambda ctx: "load" in ctx,
        evaluate_fn=_dedicated_circuit_high_power,
    ),
    ElectricalRule(
        rule_code="RULE-WET-AREA-SOCKET-CLEARANCE",
        standard="NBR 5410",
        version="MVP-interno-v1",
        category="seguranca",
        title="Distância mínima de tomadas em relação a fontes de água em áreas molhadas",
        default_severity="VERMELHO",
        applies_when=lambda ctx: "socket_placement_request" in ctx,
        evaluate_fn=_wet_area_socket_clearance,
    ),
    ElectricalRule(
        rule_code="RULE-MIN-CONDUCTOR-SECTION",
        standard="NBR 5410",
        version="MVP-interno-v1",
        category="dimensionamento",
        title="Seção mínima de condutor por tipo de circuito",
        default_severity="VERMELHO",
        applies_when=lambda ctx: "circuit" in ctx and "conductor" in ctx,
        evaluate_fn=_min_conductor_section,
    ),
    ElectricalRule(
        rule_code="RULE-DR-PROTECTION-REQUIRED",
        standard="NBR 5410",
        version="MVP-interno-v1",
        category="protecao",
        title="Quadro deve possuir dispositivo DR",
        default_severity="VERMELHO",
        applies_when=lambda ctx: "panel" in ctx and "protection_devices" in ctx,
        evaluate_fn=_dr_protection_required,
    ),
    ElectricalRule(
        rule_code="RULE-GROUNDING-REVIEW",
        standard="NBR 5410",
        version="MVP-interno-v1",
        category="aterramento",
        title="Aterramento sempre requer revisão profissional",
        default_severity="AZUL",
        applies_when=lambda ctx: "panel" in ctx and ctx.get("check_grounding"),
        evaluate_fn=_grounding_professional_review,
    ),
]
