from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Company, Country, Opportunity, Sector, TriggerDef
from app.schemas.opportunities import OpportunityIn, OpportunityOut, OpportunityStatusUpdate, OpportunityWithRelations

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _with_relations(db: Session, opp: Opportunity) -> OpportunityWithRelations:
    company = db.get(Company, opp.company_id) if opp.company_id else None
    country = db.get(Country, opp.country_code) if opp.country_code else None
    sector = db.get(Sector, opp.sector_id) if opp.sector_id else None
    trigger = db.get(TriggerDef, opp.trigger_id) if opp.trigger_id else None
    return OpportunityWithRelations(
        **OpportunityOut.model_validate(opp).model_dump(),
        company_name=company.name if company else None,
        country_name=country.name if country else None,
        sector_name=sector.name if sector else None,
        trigger_name=trigger.name if trigger else None,
    )


@router.get("", response_model=list[OpportunityWithRelations])
def list_opportunities(
    country_code: str | None = None,
    sector_id: int | None = None,
    trigger_id: int | None = None,
    status: str | None = None,
    min_score: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Opportunity)
    if country_code:
        query = query.filter(Opportunity.country_code == country_code)
    if sector_id:
        query = query.filter(Opportunity.sector_id == sector_id)
    if trigger_id:
        query = query.filter(Opportunity.trigger_id == trigger_id)
    if status:
        query = query.filter(Opportunity.status == status)
    if min_score is not None:
        query = query.filter(Opportunity.opportunity_score >= min_score)

    opportunities = query.order_by(Opportunity.opportunity_score.desc()).limit(300).all()
    return [_with_relations(db, o) for o in opportunities]


@router.post("", response_model=OpportunityOut)
def create_opportunity(payload: OpportunityIn, db: Session = Depends(get_db)):
    opportunity = Opportunity(**payload.model_dump())
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.get("/{opportunity_id}", response_model=OpportunityWithRelations)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    opportunity = db.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunité introuvable")
    return _with_relations(db, opportunity)


@router.patch("/{opportunity_id}/status", response_model=OpportunityOut)
def update_status(opportunity_id: int, payload: OpportunityStatusUpdate, db: Session = Depends(get_db)):
    opportunity = db.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunité introuvable")
    opportunity.status = payload.status
    db.commit()
    db.refresh(opportunity)
    return opportunity
