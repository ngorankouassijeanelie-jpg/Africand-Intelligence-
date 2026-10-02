from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

STAGES = [
    "detected",
    "qualified",
    "target",
    "contacted",
    "meeting",
    "proposal",
    "negotiation",
    "won",
    "client",
    "lost",
]

LOST_REASONS = ["budget", "timing", "concurrent", "aucun_besoin", "pas_de_reponse", "autre"]


class CrmDealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    opportunity_id: int
    stage: str
    estimated_value: float | None
    probability: int
    expected_close: date | None
    owner: str
    next_action: str
    lost_reason: str | None
    created_at: datetime
    updated_at: datetime


class CrmDealIn(BaseModel):
    opportunity_id: int
    stage: str = "detected"
    estimated_value: float | None = None
    probability: int = 10
    expected_close: date | None = None
    owner: str = ""
    next_action: str = ""


class CrmDealUpdate(BaseModel):
    stage: str | None = None
    estimated_value: float | None = None
    probability: int | None = None
    expected_close: date | None = None
    owner: str | None = None
    next_action: str | None = None
    lost_reason: str | None = None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    opportunity_id: int
    type: str
    channel: str
    recipient: str
    message: str
    sent_at: datetime
    status: str
