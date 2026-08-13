import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Load(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An electrical load (equipment) assigned to a room."""

    __tablename__ = "loads"

    room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    circuit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("circuits.id"), nullable=True
    )
    category: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    nominal_power_w: Mapped[float] = mapped_column(Float)
    voltage_v: Mapped[float] = mapped_column(Float, default=127.0)
    power_factor: Mapped[float] = mapped_column(Float, default=1.0)
    phase: Mapped[str] = mapped_column(String, default="single")
    demand_factor: Mapped[float] = mapped_column(Float, default=1.0)
    requires_dedicated_circuit: Mapped[bool] = mapped_column(default=False)
    source: Mapped[str] = mapped_column(String, default="catalog")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)

    room: Mapped["Room"] = relationship(back_populates="loads")  # noqa: F821
    circuit: Mapped["Circuit | None"] = relationship(back_populates="loads")


class Circuit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "circuits"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"))
    panel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("panels.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String)
    circuit_type: Mapped[str] = mapped_column(String)
    voltage_v: Mapped[float] = mapped_column(Float, default=127.0)
    phase: Mapped[str] = mapped_column(String, default="single")

    loads: Mapped[list["Load"]] = relationship(back_populates="circuit")
    panel: Mapped["Panel | None"] = relationship(back_populates="circuits")
    conductor: Mapped["Conductor | None"] = relationship(
        back_populates="circuit", uselist=False, cascade="all, delete-orphan"
    )
    breaker: Mapped["Breaker | None"] = relationship(
        back_populates="circuit", uselist=False, cascade="all, delete-orphan"
    )
    calculations: Mapped[list["Calculation"]] = relationship(  # noqa: F821
        back_populates="circuit"
    )


class Panel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "panels"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String, default="QDC-01")
    supply_voltage_v: Mapped[float] = mapped_column(Float, default=127.0)
    supply_phase: Mapped[str] = mapped_column(String, default="single")
    total_slots: Mapped[int] = mapped_column(default=24)

    circuits: Mapped[list["Circuit"]] = relationship(back_populates="panel")
    protection_devices: Mapped[list["ProtectionDevice"]] = relationship(
        back_populates="panel", cascade="all, delete-orphan"
    )


class Conductor(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "conductors"

    circuit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("circuits.id"), unique=True
    )
    material: Mapped[str] = mapped_column(String, default="copper")
    cross_section_mm2: Mapped[float] = mapped_column(Float)
    insulation: Mapped[str] = mapped_column(String, default="PVC")
    installation_method: Mapped[str] = mapped_column(String)
    ampacity_a: Mapped[float] = mapped_column(Float)
    voltage_drop_pct: Mapped[float] = mapped_column(Float)

    circuit: Mapped["Circuit"] = relationship(back_populates="conductor")


class Breaker(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "breakers"

    circuit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("circuits.id"), unique=True
    )
    rated_current_a: Mapped[float] = mapped_column(Float)
    curve: Mapped[str] = mapped_column(String, default="C")
    poles: Mapped[int] = mapped_column(default=1)

    circuit: Mapped["Circuit"] = relationship(back_populates="breaker")


class ProtectionDevice(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "protection_devices"

    panel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("panels.id"))
    device_type: Mapped[str] = mapped_column(String)  # DR, DPS, disjuntor_geral
    rated_current_a: Mapped[float | None] = mapped_column(Float, nullable=True)
    sensitivity_ma: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    panel: Mapped["Panel"] = relationship(back_populates="protection_devices")
