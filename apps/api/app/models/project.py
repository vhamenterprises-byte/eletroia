import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="OWNER")

    projects: Mapped[list["Project"]] = relationship(back_populates="owner")


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    property_type: Mapped[str] = mapped_column(String, default="residencial")
    supply_voltage: Mapped[str | None] = mapped_column(String, nullable=True)
    utility_company: Mapped[str | None] = mapped_column(String, nullable=True)
    resident_count: Mapped[int | None] = mapped_column(nullable=True)
    is_renovation: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String, default="draft")
    interview_state: Mapped[dict] = mapped_column(JSONB, default=dict)

    owner: Mapped["User"] = relationship(back_populates="projects")
    rooms: Mapped[list["Room"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Room(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "rooms"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String)
    room_type: Mapped[str] = mapped_column(String)
    area_m2: Mapped[float | None] = mapped_column(Float, nullable=True)
    perimeter_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String, default="manual_entry")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)

    project: Mapped["Project"] = relationship(back_populates="rooms")
    loads: Mapped[list["Load"]] = relationship(back_populates="room", cascade="all, delete-orphan")
