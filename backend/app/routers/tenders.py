from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Country, Sector, Tender
from app.modules.scoring.engine import score_tender_fit
from app.schemas.tenders import TenderIn, TenderOut

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.get("", response_model=list[TenderOut])
def list_tenders(
    country_code: str | None = None,
    sector_id: int | None = None,
    status: str | None = None,
    min_fit: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Tender)
    if country_code:
        query = query.filter(Tender.country_code == country_code)
    if sector_id:
        query = query.filter(Tender.sector_id == sector_id)
    if status:
        query = query.filter(Tender.status == status)
    if min_fit is not None:
        query = query.filter(Tender.fit_score >= min_fit)
    return query.order_by(Tender.fit_score.desc(), Tender.deadline.asc()).all()


@router.post("", response_model=TenderOut)
def create_tender(payload: TenderIn, db: Session = Depends(get_db)):
    sector = db.get(Sector, payload.sector_id) if payload.sector_id else None
    country = db.get(Country, payload.country_code) if payload.country_code else None
    fit_score = score_tender_fit(sector, bool(country and country.active), bool(payload.budget))

    tender = Tender(**payload.model_dump(), fit_score=fit_score)
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return tender


@router.get("/{tender_id}", response_model=TenderOut)
def get_tender(tender_id: int, db: Session = Depends(get_db)):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Appel d'offres introuvable")
    return tender


@router.patch("/{tender_id}/status", response_model=TenderOut)
def update_tender_status(tender_id: int, status: str, db: Session = Depends(get_db)):
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Appel d'offres introuvable")
    tender.status = status
    db.commit()
    db.refresh(tender)
    return tender
