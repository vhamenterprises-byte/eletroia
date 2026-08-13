"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "normative_references",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("standard", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("section", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("internal_summary", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
    )

    op.create_table(
        "rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rule_code", sa.String(), nullable=False),
        sa.Column("standard", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("default_severity", sa.String(), nullable=False),
        sa.Column(
            "normative_reference_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("normative_references.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_rules_rule_code", "rules", ["rule_code"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("property_type", sa.String(), nullable=False),
        sa.Column("supply_voltage", sa.String(), nullable=True),
        sa.Column("utility_company", sa.String(), nullable=True),
        sa.Column("resident_count", sa.Integer(), nullable=True),
        sa.Column("is_renovation", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("interview_state", postgresql.JSONB(), nullable=False),
    )

    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("room_type", sa.String(), nullable=False),
        sa.Column("area_m2", sa.Float(), nullable=True),
        sa.Column("perimeter_m", sa.Float(), nullable=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
    )

    op.create_table(
        "panels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("supply_voltage_v", sa.Float(), nullable=False),
        sa.Column("supply_phase", sa.String(), nullable=False),
        sa.Column("total_slots", sa.Integer(), nullable=False),
    )

    op.create_table(
        "circuits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("panel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("panels.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("circuit_type", sa.String(), nullable=False),
        sa.Column("voltage_v", sa.Float(), nullable=False),
        sa.Column("phase", sa.String(), nullable=False),
    )

    op.create_table(
        "loads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("circuit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("circuits.id"), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("nominal_power_w", sa.Float(), nullable=False),
        sa.Column("voltage_v", sa.Float(), nullable=False),
        sa.Column("power_factor", sa.Float(), nullable=False),
        sa.Column("phase", sa.String(), nullable=False),
        sa.Column("demand_factor", sa.Float(), nullable=False),
        sa.Column("requires_dedicated_circuit", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
    )

    op.create_table(
        "conductors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("circuit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("circuits.id"), nullable=False, unique=True),
        sa.Column("material", sa.String(), nullable=False),
        sa.Column("cross_section_mm2", sa.Float(), nullable=False),
        sa.Column("insulation", sa.String(), nullable=False),
        sa.Column("installation_method", sa.String(), nullable=False),
        sa.Column("ampacity_a", sa.Float(), nullable=False),
        sa.Column("voltage_drop_pct", sa.Float(), nullable=False),
    )

    op.create_table(
        "breakers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("circuit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("circuits.id"), nullable=False, unique=True),
        sa.Column("rated_current_a", sa.Float(), nullable=False),
        sa.Column("curve", sa.String(), nullable=False),
        sa.Column("poles", sa.Integer(), nullable=False),
    )

    op.create_table(
        "protection_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("panel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("panels.id"), nullable=False),
        sa.Column("device_type", sa.String(), nullable=False),
        sa.Column("rated_current_a", sa.Float(), nullable=True),
        sa.Column("sensitivity_ma", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
    )

    op.create_table(
        "calculations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("circuit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("circuits.id"), nullable=True),
        sa.Column("calc_type", sa.String(), nullable=False),
        sa.Column("formula", sa.String(), nullable=False),
        sa.Column("inputs", postgresql.JSONB(), nullable=False),
        sa.Column("result", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
    )

    op.create_table(
        "rule_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("rule_code", sa.String(), nullable=False),
        sa.Column("subject_type", sa.String(), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_rule_results_rule_code", "rule_results", ["rule_code"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("old_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("calculation_changed", sa.Boolean(), nullable=False),
        sa.Column("rules_changed", sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("rule_results")
    op.drop_table("calculations")
    op.drop_table("protection_devices")
    op.drop_table("breakers")
    op.drop_table("conductors")
    op.drop_table("loads")
    op.drop_table("circuits")
    op.drop_table("panels")
    op.drop_table("rooms")
    op.drop_table("projects")
    op.drop_table("rules")
    op.drop_table("normative_references")
    op.drop_table("users")
