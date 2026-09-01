from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(120), index=True)
    contact_name: Mapped[str] = mapped_column(String(100), default="")
    email: Mapped[str] = mapped_column(String(160), default="")
    website: Mapped[str] = mapped_column(String(240), default="")
    industry: Mapped[str] = mapped_column(String(100), index=True)
    location: Mapped[str] = mapped_column(String(100), default="")
    company_size: Mapped[str] = mapped_column(String(30), default="small")
    need: Mapped[str] = mapped_column(Text, default="")
    stage: Mapped[str] = mapped_column(String(30), default="New", index=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    estimated_value: Mapped[float] = mapped_column(Float, default=0)
    next_follow_up: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    outreach_draft: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="Medium")
    completed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class AutomationRun(Base):
    __tablename__ = "automation_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    business_type: Mapped[str] = mapped_column(String(100), index=True)
    business_name: Mapped[str] = mapped_column(String(140), default="My Business")
    goal: Mapped[str] = mapped_column(Text)
    channels: Mapped[str] = mapped_column(Text, default="")
    plan_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="plan_ready")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
