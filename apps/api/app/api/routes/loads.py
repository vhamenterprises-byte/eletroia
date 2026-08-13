import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engineering.standards.load_catalog import LOAD_CATALOG, find_catalog_entry
from app.models.project import Room
from app.models.electrical import Load
from app.schemas.schemas import LoadCreateCustom, LoadCreateFromCatalog, LoadOut

router = APIRouter(tags=["loads"])


@router.get("/catalog/loads")
def list_catalog():
    return [
        {
            "code": e.code,
            "category": e.category,
            "name": e.name,
            "typical_power_w": e.typical_power_w,
            "voltage_v": e.voltage_v,
            "requires_dedicated_circuit": e.requires_dedicated_circuit,
            "confidence": e.confidence,
            "source": e.source,
        }
        for e in LOAD_CATALOG
    ]


@router.post("/loads/from-catalog", response_model=list[LoadOut])
def add_load_from_catalog(payload: LoadCreateFromCatalog, db: Session = Depends(get_db)):
    room = db.get(Room, payload.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Ambiente não encontrado")
    entry = find_catalog_entry(payload.catalog_code)
    if entry is None:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado no catálogo")

    power = payload.override_power_w if payload.override_power_w is not None else entry.typical_power_w
    source = "user_override" if payload.override_power_w is not None else entry.source
    confidence = 1.0 if payload.override_power_w is not None else entry.confidence

    created = []
    for _ in range(max(1, payload.quantity)):
        load = Load(
            room_id=room.id,
            category=entry.category,
            name=entry.name,
            nominal_power_w=power,
            voltage_v=entry.voltage_v,
            demand_factor=entry.demand_factor,
            requires_dedicated_circuit=entry.requires_dedicated_circuit,
            source=source,
            confidence_score=confidence,
        )
        db.add(load)
        created.append(load)
    db.commit()
    for load in created:
        db.refresh(load)
    return created


@router.post("/loads/custom", response_model=LoadOut)
def add_custom_load(payload: LoadCreateCustom, db: Session = Depends(get_db)):
    room = db.get(Room, payload.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Ambiente não encontrado")
    load = Load(
        room_id=room.id,
        category=payload.category,
        name=payload.name,
        nominal_power_w=payload.nominal_power_w,
        voltage_v=payload.voltage_v,
        power_factor=payload.power_factor,
        phase=payload.phase,
        demand_factor=payload.demand_factor,
        requires_dedicated_circuit=payload.requires_dedicated_circuit,
        source="user_custom",
        confidence_score=1.0,
    )
    db.add(load)
    db.commit()
    db.refresh(load)
    return load


@router.get("/rooms/{room_id}/loads", response_model=list[LoadOut])
def list_room_loads(room_id: uuid.UUID, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Ambiente não encontrado")
    return room.loads
