import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class RuleGroup(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rule_groups"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    rules = sa.orm.relationship("Rule", back_populates="group", cascade="all, delete-orphan")


class Rule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rules"

    group_id = mapped_column(sa.Uuid, sa.ForeignKey("rule_groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    stop_processing: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    group = sa.orm.relationship("RuleGroup", back_populates="rules")
    triggers = sa.orm.relationship("RuleTrigger", back_populates="rule", cascade="all, delete-orphan")
    actions = sa.orm.relationship("RuleAction", back_populates="rule", cascade="all, delete-orphan")


class RuleTrigger(Base, UUIDMixin):
    __tablename__ = "rule_triggers"

    rule_id = mapped_column(sa.Uuid, sa.ForeignKey("rules.id"), nullable=False)
    trigger_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    value: Mapped[str] = mapped_column(sa.Text, nullable=False)
    is_negated: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)

    rule = sa.orm.relationship("Rule", back_populates="triggers")


class RuleAction(Base, UUIDMixin):
    __tablename__ = "rule_actions"

    rule_id = mapped_column(sa.Uuid, sa.ForeignKey("rules.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    value: Mapped[str | None] = mapped_column(sa.Text)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)

    rule = sa.orm.relationship("Rule", back_populates="actions")
