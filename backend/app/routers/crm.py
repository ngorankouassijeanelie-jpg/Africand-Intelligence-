from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import CrmDeal, Opportunity
from app.schemas.crm import CrmDealIn, CrmDealOut, CrmDealUpdate

router = APIRouter(prefix="/crm/deals", tags=["crm"])


@router.get("", response_model=list[CrmDealOut])
def list_deals(stage: str | None = None, db: Session = Depends(get_db)):
    query = db.query(CrmDeal)
    if stage:
        query = query.filter(CrmDeal.stage == stage)
    return query.order_by(CrmDeal.updated_at.desc()).all()


@router.post("", response_model=CrmDealOut)
def create_deal(payload: CrmDealIn, db: Session = Depends(get_db)):
    opportunity = db.get(Opportunity, payload.opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunité introuvable")
    existing = db.query(CrmDeal).filter(CrmDeal.opportunity_id == payload.opportunity_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un deal CRM existe déjà pour cette opportunité")

    deal = CrmDeal(**payload.model_dump())
    db.add(deal)
    opportunity.status = payload.stage
    db.commit()
    db.refresh(deal)
    return deal


@router.patch("/{deal_id}", response_model=CrmDealOut)
def update_deal(deal_id: int, payload: CrmDealUpdate, db: Session = Depends(get_db)):
    deal = db.get(CrmDeal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal introuvable")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(deal, key, value)

    if payload.stage:
        opportunity = db.get(Opportunity, deal.opportunity_id)
        if opportunity:
            opportunity.status = payload.stage

    db.commit()
    db.refresh(deal)
    return deal


@router.get("/pipeline/summary")
def pipeline_summary(db: Session = Depends(get_db)):
    deals = db.query(CrmDeal).all()
    summary: dict[str, dict] = {}
    for deal in deals:
        bucket = summary.setdefault(deal.stage, {"count": 0, "value": 0.0})
        bucket["count"] += 1
        bucket["value"] += deal.estimated_value or 0
    return summary
