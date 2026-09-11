from datetime import datetime, date
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_text: Mapped[str] = mapped_column(Text)
    report_type: Mapped[str] = mapped_column(String(40), index=True)
    location: Mapped[str] = mapped_column(String(120), index=True)
    department: Mapped[str] = mapped_column(String(100), index=True)
    activity: Mapped[str] = mapped_column(String(120), default="General Operations")
    sif_label: Mapped[str] = mapped_column(String(30), default="Non-SIF-Potential", index=True)
    sif_probability: Mapped[float] = mapped_column(Float, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW", index=True)
    life_saving_rule: Mapped[str] = mapped_column(String(100), default="Other")
    barrier_failure: Mapped[str] = mapped_column(String(160), default="Not identified")
    potential_consequence: Mapped[str] = mapped_column(String(240), default="No serious consequence identified")
    status: Mapped[str] = mapped_column(String(30), default="Pending Review", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    analyses: Mapped[list["AIAnalysis"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    actions: Mapped[list["CorrectiveAction"]] = relationship(back_populates="report", cascade="all, delete-orphan")


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
    explanation: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(60), default="tfidf-logistic-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    report: Mapped[Report] = relationship(back_populates="analyses")


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
    severity: Mapped[str] = mapped_column(String(20), default="HIGH")
    status: Mapped[str] = mapped_column(String(30), default="Open")
    acknowledged_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    report: Mapped[Report] = relationship()


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int | None] = mapped_column(ForeignKey("reports.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    responsible: Mapped[str] = mapped_column(String(120))
    priority: Mapped[str] = mapped_column(String(20), default="Medium")
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="Open")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    report: Mapped[Report | None] = relationship(back_populates="actions")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(40))
