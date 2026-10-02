from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, get_current_admin, verify_password
from app.db.models import Country, ScoringWeight, Sector, Source, TriggerDef, User
from app.modules.pipeline import run_full_pipeline
from app.modules.scoring.engine import ensure_default_weights
from app.schemas.admin import IngestRunResult, LoginIn, LoginOut
from app.schemas.common import (
    CountryIn,
    CountryOut,
    ScoringWeightIn,
    ScoringWeightOut,
    SectorIn,
    SectorOut,
    SourceIn,
    SourceOut,
    TriggerIn,
    TriggerOut,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    settings = get_settings()
    user = db.query(User).filter(User.email == payload.email).first()

    if user is None and payload.email == settings.admin_email and payload.password == settings.admin_password:
        return LoginOut(access_token=create_access_token(payload.email))

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    return LoginOut(access_token=create_access_token(user.email))


# --- Sources ---
@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.name).all()


@router.post("/sources", response_model=SourceOut)
def create_source(payload: SourceIn, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    source = Source(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/sources/{source_id}")
def delete_source(source_id: int, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    source = db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source introuvable")
    db.delete(source)
    db.commit()
    return {"ok": True}


# --- Sectors ---
@router.get("/sectors", response_model=list[SectorOut])
def list_sectors(db: Session = Depends(get_db)):
    return db.query(Sector).order_by(Sector.priority, Sector.name).all()


@router.post("/sectors", response_model=SectorOut)
def create_sector(payload: SectorIn, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    sector = Sector(**payload.model_dump())
    db.add(sector)
    db.commit()
    db.refresh(sector)
    return sector


@router.delete("/sectors/{sector_id}")
def delete_sector(sector_id: int, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    sector = db.get(Sector, sector_id)
    if not sector:
        raise HTTPException(status_code=404, detail="Secteur introuvable")
    db.delete(sector)
    db.commit()
    return {"ok": True}


# --- Countries ---
@router.get("/countries", response_model=list[CountryOut])
def list_countries_admin(db: Session = Depends(get_db)):
    return db.query(Country).order_by(Country.phase, Country.name).all()


@router.post("/countries", response_model=CountryOut)
def create_country(payload: CountryIn, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    country = Country(**payload.model_dump())
    db.add(country)
    db.commit()
    db.refresh(country)
    return country


# --- Triggers ---
@router.get("/triggers", response_model=list[TriggerOut])
def list_triggers(db: Session = Depends(get_db)):
    return db.query(TriggerDef).order_by(TriggerDef.name).all()


@router.post("/triggers", response_model=TriggerOut)
def create_trigger(payload: TriggerIn, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    trigger = TriggerDef(**payload.model_dump())
    db.add(trigger)
    db.commit()
    db.refresh(trigger)
    return trigger


@router.put("/triggers/{trigger_id}", response_model=TriggerOut)
def update_trigger(
    trigger_id: int, payload: TriggerIn, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)
):
    trigger = db.get(TriggerDef, trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger introuvable")
    for key, value in payload.model_dump().items():
        setattr(trigger, key, value)
    db.commit()
    db.refresh(trigger)
    return trigger


@router.delete("/triggers/{trigger_id}")
def delete_trigger(trigger_id: int, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    trigger = db.get(TriggerDef, trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger introuvable")
    db.delete(trigger)
    db.commit()
    return {"ok": True}


# --- Scoring weights ---
@router.get("/scoring-weights", response_model=list[ScoringWeightOut])
def list_scoring_weights(db: Session = Depends(get_db)):
    ensure_default_weights(db)
    return db.query(ScoringWeight).all()


@router.put("/scoring-weights/{criterion}", response_model=ScoringWeightOut)
def update_scoring_weight(
    criterion: str, payload: ScoringWeightIn, admin: str = Depends(get_current_admin), db: Session = Depends(get_db)
):
    weight = db.get(ScoringWeight, criterion)
    if not weight:
        raise HTTPException(status_code=404, detail="Critère de pondération introuvable")
    weight.weight_percent = payload.weight_percent
    db.commit()
    db.refresh(weight)
    return weight


# --- Ingestion ---
@router.post("/ingest/run", response_model=IngestRunResult)
def run_ingestion(admin: str = Depends(get_current_admin), db: Session = Depends(get_db)):
    result = run_full_pipeline(db)
    return IngestRunResult(**result)
