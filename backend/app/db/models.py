from datetime import datetime, date

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    phase: Mapped[int] = mapped_column(Integer, default=1)  # 1, 2 ou 3 (voir perimetre geographique)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Sector(Base):
    __tablename__ = "sectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    priority: Mapped[int] = mapped_column(Integer, default=2)  # 1 = prioritaire, 2 = secondaire
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class TriggerDef(Base):
    __tablename__ = "triggers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    potential_services: Mapped[list] = mapped_column(JSON, default=list)
    base_need_score: Mapped[int] = mapped_column(Integer, default=50)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(500))
    country_code: Mapped[str | None] = mapped_column(ForeignKey("countries.code"), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="media")  # media, institution, tender, corporate
    reliability_score: Mapped[int] = mapped_column(Integer, default=70)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RawItem(Base):
    """Information brute collectee avant traitement IA (data_collection -> data_processing)."""

    __tablename__ = "raw_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(String(1000))
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)

    source: Mapped["Source"] = relationship()


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300), index=True)
    country_code: Mapped[str | None] = mapped_column(ForeignKey("countries.code"), nullable=True)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sectors.id"), nullable=True)
    website: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    revenue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employees: Mapped[str | None] = mapped_column(String(50), nullable=True)
    executives: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    country: Mapped["Country"] = relationship()
    sector: Mapped["Sector"] = relationship()


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    name: Mapped[str] = mapped_column(String(200))
    position: Mapped[str] = mapped_column(String(150))
    source: Mapped[str] = mapped_column(String(500), default="")
    public_profile: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verification_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    company: Mapped["Company"] = relationship()


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    trigger_id: Mapped[int | None] = mapped_column(ForeignKey("triggers.id"), nullable=True)
    raw_item_id: Mapped[int | None] = mapped_column(ForeignKey("raw_items.id"), nullable=True)

    description: Mapped[str] = mapped_column(Text, default="")
    country_code: Mapped[str | None] = mapped_column(ForeignKey("countries.code"), nullable=True)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sectors.id"), nullable=True)

    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    related_sources: Mapped[list] = mapped_column(JSON, default=list)  # dedup: autres sources du meme evenement

    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    opportunity_score: Mapped[int] = mapped_column(Integer, default=0)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    urgency: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    suggested_service: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)

    status: Mapped[str] = mapped_column(String(30), default="detected")
    # detected, qualified, target, contacted, meeting, proposal, negotiation, won, client, lost

    company: Mapped["Company"] = relationship()
    trigger: Mapped["TriggerDef"] = relationship()
    country: Mapped["Country"] = relationship()
    sector: Mapped["Sector"] = relationship()
    source: Mapped["Source"] = relationship()


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    institution: Mapped[str] = mapped_column(String(300))
    country_code: Mapped[str | None] = mapped_column(ForeignKey("countries.code"), nullable=True)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sectors.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    budget: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    fit_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="open")  # open, closed, won, lost
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    country: Mapped["Country"] = relationship()
    sector: Mapped["Sector"] = relationship()


class Investor(Base):
    __tablename__ = "investors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    type: Mapped[str] = mapped_column(String(100), default="")  # PE, VC, family office, DFI...
    countries: Mapped[list] = mapped_column(JSON, default=list)
    sectors: Mapped[list] = mapped_column(JSON, default=list)
    ticket_size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recent_activity: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    category: Mapped[str] = mapped_column(String(100), default="")  # cabinet, banque, fonds, juridique...
    countries: Mapped[list] = mapped_column(JSON, default=list)
    sectors: Mapped[list] = mapped_column(JSON, default=list)
    description: Mapped[str] = mapped_column(Text, default="")
    contact_info: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id"))
    type: Mapped[str] = mapped_column(String(30), default="priority")  # priority, high, tender
    channel: Mapped[str] = mapped_column(String(30), default="dashboard")
    recipient: Mapped[str] = mapped_column(String(200), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="sent")

    opportunity: Mapped["Opportunity"] = relationship()


class CrmDeal(Base):
    __tablename__ = "crm_deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id"), unique=True)
    stage: Mapped[str] = mapped_column(String(30), default="detected")
    estimated_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    probability: Mapped[int] = mapped_column(Integer, default=10)
    expected_close: Mapped[date | None] = mapped_column(Date, nullable=True)
    owner: Mapped[str] = mapped_column(String(200), default="")
    next_action: Mapped[str] = mapped_column(Text, default="")
    lost_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    opportunity: Mapped["Opportunity"] = relationship()


class ScoringWeight(Base):
    __tablename__ = "scoring_weights"

    criterion: Mapped[str] = mapped_column(String(50), primary_key=True)
    weight_percent: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(150), default="")


class AdminSetting(Base):
    __tablename__ = "admin_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, default=dict)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(30), default="admin")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
