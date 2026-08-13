import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engineering.orchestrator import generate_electrical_design
from app.engineering.rules.engine import RulesEngine
from app.engineering.rules.nbr5410 import NBR5410_RULES
from app.models.engineering import Calculation, RuleResult
from app.models.project import Project, Room
from app.schemas.schemas import (
    ProjectCreate,
    ProjectOut,
    RoomCreate,
    RoomOut,
    RuleResultOut,
    SocketPlacementCheckRequest,
)

router = APIRouter(prefix="/projects", tags=["projects"])
rules_engine = RulesEngine(NBR5410_RULES)


def _get_project_or_404(db: Session, project_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project


@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return _get_project_or_404(db, project_id)


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.post("/{project_id}/rooms", response_model=RoomOut)
def add_room(project_id: uuid.UUID, payload: RoomCreate, db: Session = Depends(get_db)):
    project = _get_project_or_404(db, project_id)
    room = Room(project_id=project.id, **payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/{project_id}/rooms", response_model=list[RoomOut])
def list_rooms(project_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_project_or_404(db, project_id)
    return db.query(Room).filter(Room.project_id == project_id).all()


@router.post("/{project_id}/socket-placement-check", response_model=RuleResultOut)
def check_socket_placement(
    project_id: uuid.UUID, payload: SocketPlacementCheckRequest, db: Session = Depends(get_db)
):
    """Verificação pontual — exemplo do prompt mestre (seção 14): pedido de tomada dentro
    do box do chuveiro deve ser recusado, não aceito silenciosamente."""
    _get_project_or_404(db, project_id)
    request_id = str(uuid.uuid4())
    context = {
        "socket_placement_request": {
            "id": request_id,
            "room_type": payload.room_type,
            "distance_from_water_source_m": payload.distance_from_water_source_m,
        }
    }
    result = rules_engine.evaluate_one("RULE-WET-AREA-SOCKET-CLEARANCE", context)
    if result is None:
        raise HTTPException(status_code=500, detail="Regra não encontrada")
    return RuleResultOut(
        rule_code=result.rule_code,
        status=result.status,
        message=result.message,
        subject_type=result.subject_type,
        subject_id=result.subject_id,
    )


@router.post("/{project_id}/generate")
def generate_design(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = _get_project_or_404(db, project_id)
    if not project.rooms:
        raise HTTPException(
            status_code=400, detail="Cadastre ao menos um ambiente antes de gerar o projeto."
        )
    summary = generate_electrical_design(db, project)
    project.status = "generated"
    db.commit()
    return summary


@router.get("/{project_id}/rule-results", response_model=list[RuleResultOut])
def get_rule_results(project_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_project_or_404(db, project_id)
    rows = db.query(RuleResult).filter(RuleResult.project_id == project_id).all()
    return [
        RuleResultOut(
            rule_code=r.rule_code,
            status=r.status,
            message=r.message,
            subject_type=r.subject_type,
            subject_id=str(r.subject_id) if r.subject_id else None,
        )
        for r in rows
    ]


@router.get("/{project_id}/compliance-summary")
def get_compliance_summary(project_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_project_or_404(db, project_id)
    rows = db.query(RuleResult).filter(RuleResult.project_id == project_id).all()
    counts = {"VERDE": 0, "AMARELO": 0, "VERMELHO": 0, "AZUL": 0}
    for r in rows:
        counts[r.status] = counts.get(r.status, 0) + 1
    return {
        "counts": counts,
        "note": (
            "Verificações automáticas realizadas com base nas regras técnicas configuradas "
            "nesta plataforma. Isto não substitui a aprovação de um profissional habilitado."
        ),
    }


@router.get("/{project_id}/calculations")
def get_calculations(project_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_project_or_404(db, project_id)
    rows = db.query(Calculation).filter(Calculation.project_id == project_id).all()
    return [
        {
            "id": str(r.id),
            "circuit_id": str(r.circuit_id) if r.circuit_id else None,
            "calc_type": r.calc_type,
            "formula": r.formula,
            "inputs": r.inputs,
            "result": r.result,
            "unit": r.unit,
            "source": r.source,
        }
        for r in rows
    ]
