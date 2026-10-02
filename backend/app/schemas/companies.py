from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    name: str
    position: str
    source: str
    public_profile: str | None
    verification_date: date | None


class ContactIn(BaseModel):
    name: str
    position: str
    source: str = ""
    public_profile: str | None = None
    verification_date: date | None = None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    country_code: str | None
    sector_id: int | None
    website: str | None
    description: str
    size: str | None
    revenue: str | None
    employees: str | None
    executives: list
    created_at: datetime
    updated_at: datetime


class CompanyIn(BaseModel):
    name: str
    country_code: str | None = None
    sector_id: int | None = None
    website: str | None = None
    description: str = ""
    size: str | None = None
    revenue: str | None = None
    employees: str | None = None
    executives: list = []


class CompanyDetail(CompanyOut):
    contacts: list[ContactOut] = []
    opportunity_count: int = 0
    commercial_score: int = 0
