import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.documents.pdf_report import build_project_pdf
from app.models.electrical import Circuit
from app.models.engineering import RuleResult
from app.models.project import Project

router = APIRouter(prefix="/projects", tags=["documents"])


@router.get("/{project_id}/document.pdf")
def get_project_pdf(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    circuits = db.query(Circuit).filter(Circuit.project_id == project_id).all()
    rule_results = db.query(RuleResult).filter(RuleResult.project_id == project_id).all()

    pdf_bytes = build_project_pdf(project, circuits, rule_results)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{project.name}.pdf"'},
    )
