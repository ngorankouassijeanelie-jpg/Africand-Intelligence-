from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    phase: int
    active: bool


class CountryIn(BaseModel):
    code: str
    name: str
    phase: int = 1
    active: bool = True


class SectorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    priority: int
    active: bool


class SectorIn(BaseModel):
    name: str
    priority: int = 2
    active: bool = True


class TriggerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    description: str
    keywords: list[str]
    potential_services: list[str]
    base_need_score: int
    active: bool


class TriggerIn(BaseModel):
    code: str
    name: str
    description: str = ""
    keywords: list[str] = []
    potential_services: list[str] = []
    base_need_score: int = 50
    active: bool = True


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    url: str
    country_code: str | None
    category: str
    reliability_score: int
    active: bool
    created_at: datetime


class SourceIn(BaseModel):
    name: str
    url: str
    country_code: str | None = None
    category: str = "media"
    reliability_score: int = 70
    active: bool = True


class ScoringWeightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    criterion: str
    weight_percent: int
    label: str


class ScoringWeightIn(BaseModel):
    weight_percent: int


class AdminSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    value: dict
