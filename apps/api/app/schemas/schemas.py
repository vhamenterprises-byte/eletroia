import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    name: str
    role: str


class ProjectCreate(BaseModel):
    owner_id: uuid.UUID
    name: str
    address: str | None = None
    property_type: str = "residencial"
    supply_voltage: str | None = None
    utility_company: str | None = None
    resident_count: int | None = None
    is_renovation: bool = False


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    address: str | None
    property_type: str
    supply_voltage: str | None
    utility_company: str | None
    resident_count: int | None
    is_renovation: bool
    status: str
    created_at: datetime


class RoomCreate(BaseModel):
    name: str
    room_type: str
    area_m2: float | None = None
    perimeter_m: float | None = None


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    room_type: str
    area_m2: float | None
    perimeter_m: float | None
    source: str
    confidence_score: float


class LoadCreateFromCatalog(BaseModel):
    room_id: uuid.UUID
    catalog_code: str
    quantity: int = 1
    override_power_w: float | None = None


class LoadCreateCustom(BaseModel):
    room_id: uuid.UUID
    category: str
    name: str
    nominal_power_w: float
    voltage_v: float = 127.0
    power_factor: float = 1.0
    phase: str = "single"
    demand_factor: float = 1.0
    requires_dedicated_circuit: bool = False


class LoadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    room_id: uuid.UUID
    circuit_id: uuid.UUID | None
    category: str
    name: str
    nominal_power_w: float
    voltage_v: float
    power_factor: float
    phase: str
    demand_factor: float
    requires_dedicated_circuit: bool
    source: str
    confidence_score: float


class CircuitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    panel_id: uuid.UUID | None
    name: str
    circuit_type: str
    voltage_v: float
    phase: str


class ConductorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cross_section_mm2: float
    installation_method: str
    ampacity_a: float
    voltage_drop_pct: float


class BreakerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rated_current_a: float
    curve: str
    poles: int


class RuleResultOut(BaseModel):
    rule_code: str
    status: str
    message: str
    subject_type: str
    subject_id: str | None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    rule_codes_cited: list[str]
    calculation_types_cited: list[str]


class SocketPlacementCheckRequest(BaseModel):
    room_type: str
    distance_from_water_source_m: float | None = None
