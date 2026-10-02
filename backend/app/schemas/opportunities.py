from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OpportunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int | None
    trigger_id: int | None
    description: str
    country_code: str | None
    sector_id: int | None
    amount: float | None
    currency: str | None
    source_url: str
    related_sources: list
    detected_at: datetime
    opportunity_score: int
    score_breakdown: dict
    urgency: str
    suggested_service: list
    confidence: float
    status: str


class OpportunityIn(BaseModel):
    company_id: int | None = None
    trigger_id: int | None = None
    description: str
    country_code: str | None = None
    sector_id: int | None = None
    amount: float | None = None
    currency: str | None = None
    source_url: str = ""
    urgency: str = "medium"
    suggested_service: list[str] = []
    confidence: float = 0.5


class OpportunityStatusUpdate(BaseModel):
    status: str


class OpportunityWithRelations(OpportunityOut):
    company_name: str | None = None
    country_name: str | None = None
    sector_name: str | None = None
    trigger_name: str | None = None
