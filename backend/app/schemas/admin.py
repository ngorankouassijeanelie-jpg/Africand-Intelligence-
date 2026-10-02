from pydantic import BaseModel


class LoginIn(BaseModel):
    email: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class IngestRunResult(BaseModel):
    raw_items_collected: int
    opportunities_created: int
    opportunities_merged: int
    alerts_sent: int
