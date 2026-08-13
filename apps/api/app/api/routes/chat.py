import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.chat import answer_project_question
from app.ai.explain import build_explanation
from app.ai.factory import get_ai_provider
from app.ai.interview import ask_next_question, guard_user_answer
from app.core.db import get_db
from app.engineering.calculations.electrical import CalculationResult
from app.engineering.rules.engine import RuleEvaluation
from app.models.engineering import Calculation, RuleResult
from app.models.project import Project
from app.schemas.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/projects", tags=["ai"])


def _load_facts(db: Session, project_id: uuid.UUID):
    rule_rows = db.query(RuleResult).filter(RuleResult.project_id == project_id).all()
    calc_rows = db.query(Calculation).filter(Calculation.project_id == project_id).all()

    rule_evaluations = [
        RuleEvaluation(
            rule_code=r.rule_code,
            status=r.status,
            message=r.message,
            subject_type=r.subject_type,
            subject_id=str(r.subject_id) if r.subject_id else None,
            details=r.details,
        )
        for r in rule_rows
    ]
    calc_results = [
        CalculationResult(
            calc_type=c.calc_type,
            formula=c.formula,
            inputs=c.inputs,
            result=c.result,
            unit=c.unit,
            source=c.source,
        )
        for c in calc_rows
    ]
    return build_explanation(rule_evaluations, calc_results)


@router.post("/{project_id}/chat", response_model=ChatResponse)
def chat(project_id: uuid.UUID, payload: ChatRequest, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    facts = _load_facts(db, project_id)
    provider = get_ai_provider()
    reply = answer_project_question(provider, payload.message, facts)
    return ChatResponse(
        reply=reply, rule_codes_cited=facts.rule_codes, calculation_types_cited=facts.calculation_types
    )


@router.post("/{project_id}/interview/next")
def interview_next(
    project_id: uuid.UUID, last_user_answer: str | None = None, db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    if last_user_answer:
        refusal = guard_user_answer(last_user_answer)
        if refusal:
            return {"question": refusal, "blocked": True}

    room_summary = "\n".join(
        f"- {r.name} ({r.room_type}), {len(r.loads)} equipamento(s) cadastrado(s)"
        for r in project.rooms
    ) or "(nenhum ambiente cadastrado ainda)"
    state_summary = f"Projeto: {project.name}\nAmbientes:\n{room_summary}"

    provider = get_ai_provider()
    question = ask_next_question(provider, state_summary, last_user_answer)
    return {"question": question, "blocked": False}
