"""Geração do pacote de documentação (seção 32 do prompt mestre) — MVP: capa, memorial,
quadro de cargas, lista de circuitos e relatório de conformidade em um único PDF."""

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.electrical import Circuit
from app.models.engineering import RuleResult
from app.models.project import Project

STATUS_LABELS = {
    "VERDE": "Verificado automaticamente",
    "AMARELO": "Pendente de confirmação",
    "VERMELHO": "Inconsistência identificada",
    "AZUL": "Requer revisão profissional",
}


def build_project_pdf(project: Project, circuits: list[Circuit], rule_results: list[RuleResult]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    # Capa
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph(f"<b>{project.name}</b>", styles["Title"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(project.address or "Endereço não informado", styles["Normal"]))
    story.append(Paragraph(f"Tipo de imóvel: {project.property_type}", styles["Normal"]))
    story.append(
        Paragraph(f"Gerado em {datetime.now(timezone.utc).strftime('%d/%m/%Y')}", styles["Normal"])
    )
    story.append(Spacer(1, 1 * cm))
    story.append(
        Paragraph(
            "<i>Documento gerado com apoio de inteligência artificial. As verificações "
            "automáticas indicadas neste relatório são baseadas em regras técnicas "
            "configuradas na plataforma e não substituem a análise e a responsabilidade "
            "técnica de um profissional habilitado.</i>",
            styles["Normal"],
        )
    )
    story.append(PageBreak())

    # Memorial descritivo
    story.append(Paragraph("Memorial Descritivo", styles["Heading1"]))
    story.append(
        Paragraph(
            f"Este projeto elétrico residencial de baixa tensão foi elaborado com apoio da "
            f"plataforma EletroIA para o imóvel '{project.name}'"
            + (f", localizado em {project.address}" if project.address else "")
            + f". A alimentação considerada é de {project.supply_voltage or 'tensão não informada'}"
            + (f", concessionária {project.utility_company}" if project.utility_company else "")
            + ". Os circuitos foram distribuídos por ambiente, separando iluminação, tomadas "
            "de uso geral e circuitos dedicados para cargas de alta potência, conforme os "
            "critérios técnicos configurados na plataforma.",
            styles["Normal"],
        )
    )
    story.append(PageBreak())

    # Quadro de cargas / lista de circuitos
    story.append(Paragraph("Quadro de Cargas e Lista de Circuitos", styles["Heading1"]))
    table_data = [["Circuito", "Tipo", "Tensão (V)", "Condutor (mm²)", "Disjuntor (A)"]]
    for c in circuits:
        cond = f"{c.conductor.cross_section_mm2}" if c.conductor else "-"
        brk = f"{c.breaker.rated_current_a}" if c.breaker else "-"
        table_data.append([c.name, c.circuit_type, str(c.voltage_v), cond, brk])
    table = Table(table_data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(table)
    story.append(PageBreak())

    # Relatório de conformidade
    story.append(Paragraph("Relatório de Conformidade", styles["Heading1"]))
    story.append(
        Paragraph(
            "Verificações automáticas realizadas com base nas regras técnicas configuradas "
            "nesta plataforma. Isto não substitui a aprovação de um profissional habilitado.",
            styles["Normal"],
        )
    )
    counts = {"VERDE": 0, "AMARELO": 0, "VERMELHO": 0, "AZUL": 0}
    rr_data = [["Status", "Regra", "Mensagem"]]
    for r in rule_results:
        counts[r.status] = counts.get(r.status, 0) + 1
        rr_data.append([STATUS_LABELS.get(r.status, r.status), r.rule_code, r.message])
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            f"VERDE: {counts['VERDE']} | AMARELO: {counts['AMARELO']} | "
            f"VERMELHO: {counts['VERMELHO']} | AZUL (revisão profissional): {counts['AZUL']}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.3 * cm))
    rr_table = Table(rr_data, hAlign="LEFT", colWidths=[3.5 * cm, 5 * cm, 8 * cm])
    rr_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(rr_table)

    doc.build(story)
    return buffer.getvalue()
