import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class NormativeReference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Structured pointer into a standard (e.g. NBR 5410) — never the copyrighted text itself."""

    __tablename__ = "normative_references"

    standard: Mapped[str] = mapped_column(String)  # e.g. "NBR 5410"
    version: Mapped[str] = mapped_column(String)  # e.g. "2004 (vigente)"
    section: Mapped[str] = mapped_column(String)  # e.g. "9.5.2.2"
    title: Mapped[str] = mapped_column(String)
    internal_summary: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)


class Rule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Metadata for a rule implemented in app.engineering.rules — code is the source of truth
    for `evaluate()`; this row exists for traceability and lookups by id."""

    __tablename__ = "rules"

    rule_code: Mapped[str] = mapped_column(String, unique=True, index=True)
    standard: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    default_severity: Mapped[str] = mapped_column(String)
    normative_reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("normative_references.id"), nullable=True
    )


class RuleResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "rule_results"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"))
    rule_code: Mapped[str] = mapped_column(String, index=True)
    subject_type: Mapped[str] = mapped_column(String)  # room, circuit, load, project
    subject_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String)  # VERDE, AMARELO, VERMELHO, AZUL
    message: Mapped[str] = mapped_column(String)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)


class Calculation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "calculations"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"))
    circuit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("circuits.id"), nullable=True
    )
    calc_type: Mapped[str] = mapped_column(String)
    formula: Mapped[str] = mapped_column(String)
    inputs: Mapped[dict] = mapped_column(JSONB)
    result: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, default="engineering.calculations")

    circuit: Mapped["Circuit"] = relationship(back_populates="calculations")  # noqa: F821
