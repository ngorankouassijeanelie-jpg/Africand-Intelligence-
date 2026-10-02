from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    institution: str
    country_code: str | None
    sector_id: int | None
    title: str
    description: str
    budget: str | None
    deadline: date | None
    source_url: str
    fit_score: int
    status: str
    detected_at: datetime


class TenderIn(BaseModel):
    institution: str
    country_code: str | None = None
    sector_id: int | None = None
    title: str
    description: str = ""
    budget: str | None = None
    deadline: date | None = None
    source_url: str = ""


class InvestorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    type: str
    countries: list
    sectors: list
    ticket_size: str | None
    recent_activity: str


class InvestorIn(BaseModel):
    name: str
    type: str = ""
    countries: list[str] = []
    sectors: list[str] = []
    ticket_size: str | None = None
    recent_activity: str = ""


class PartnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    countries: list
    sectors: list
    description: str
    contact_info: str


class PartnerIn(BaseModel):
    name: str
    category: str = ""
    countries: list[str] = []
    sectors: list[str] = []
    description: str = ""
    contact_info: str = ""
