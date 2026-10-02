from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Company, Country, Investor, Opportunity, Tender
from app.schemas.common import CountryOut

router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("", response_model=list[CountryOut])
def list_countries(db: Session = Depends(get_db)):
    return db.query(Country).order_by(Country.phase, Country.name).all()


@router.get("/{code}")
def get_country_detail(code: str, db: Session = Depends(get_db)):
    country = db.get(Country, code.upper())
    if not country:
        raise HTTPException(status_code=404, detail="Pays introuvable")

    opportunities = (
        db.query(Opportunity)
        .filter(Opportunity.country_code == code.upper())
        .order_by(Opportunity.opportunity_score.desc())
        .limit(50)
        .all()
    )
    companies = db.query(Company).filter(Company.country_code == code.upper()).limit(50).all()
    tenders = db.query(Tender).filter(Tender.country_code == code.upper()).limit(50).all()
    investors = [i for i in db.query(Investor).all() if code.upper() in (i.countries or [])]

    return {
        "country": CountryOut.model_validate(country),
        "opportunities_count": len(opportunities),
        "top_opportunities": [
            {"id": o.id, "description": o.description, "score": o.opportunity_score, "status": o.status}
            for o in opportunities
        ],
        "companies": [{"id": c.id, "name": c.name, "sector_id": c.sector_id} for c in companies],
        "tenders": [{"id": t.id, "title": t.title, "fit_score": t.fit_score, "deadline": t.deadline} for t in tenders],
        "active_investors": [{"id": i.id, "name": i.name, "type": i.type} for i in investors],
    }
