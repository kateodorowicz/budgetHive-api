"""Budget, Activity, BudgetRevision, and DepartmentShare models."""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Budget(Base):
    """Budget document with JSON answers and budget_data."""

    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    answers = Column(JSON, nullable=True)  # JSON from frontend wizard
    budget_data = Column(JSON, nullable=True)  # Computed budget from frontend
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="budgets")
    activities = relationship("Activity", back_populates="budget", cascade="all, delete-orphan")
    revisions = relationship("BudgetRevision", back_populates="budget", cascade="all, delete-orphan")
    shares = relationship("DepartmentShare", back_populates="budget", cascade="all, delete-orphan")


class Activity(Base):
    """Activity log for a budget."""

    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    budget = relationship("Budget", back_populates="activities")


class BudgetRevision(Base):
    """Revision snapshot of a budget."""

    __tablename__ = "budget_revisions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    answers = Column(JSON, nullable=True)
    budget_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    budget = relationship("Budget", back_populates="revisions")


class DepartmentShare(Base):
    """Share link for a budget (department or external)."""

    __tablename__ = "department_shares"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    share_type = Column(String(50), nullable=True)  # e.g. "department", "external"
    permissions = Column(JSON, nullable=True)  # e.g. {"view": true, "edit": false}
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    budget = relationship("Budget", back_populates="shares")
