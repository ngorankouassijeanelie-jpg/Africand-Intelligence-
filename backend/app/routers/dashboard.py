from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Company, CrmDeal, Investor, Opportunity, Partner, Tender

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpi")
def get_kpis(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    new_opportunities = db.query(Opportunity).filter(Opportunity.detected_at >= week_ago).count()
    priority_opportunities = db.query(Opportunity).filter(Opportunity.opportunity_score >= 75).count()
    opportunities_this_week = new_opportunities
    active_tenders = db.query(Tender).filter(Tender.status == "open").count()
    companies_watched = db.query(Company).count()
    active_investors = db.query(Investor).count()
    potential_partnerships = db.query(Partner).count()

    pipeline_value = (
        db.query(CrmDeal)
        .filter(CrmDeal.stage.notin_(["lost"]))
        .all()
    )
    potential_value = sum(d.estimated_value or 0 for d in pipeline_value)

    return {
        "nouvelles_opportunites": new_opportunities,
        "opportunites_prioritaires": priority_opportunities,
        "opportunites_cette_semaine": opportunities_this_week,
        "appels_offres_actifs": active_tenders,
        "entreprises_surveillees": companies_watched,
        "investisseurs_actifs": active_investors,
        "partenariats_potentiels": potential_partnerships,
        "valeur_commerciale_potentielle": potential_value,
    }


@router.get("/top-opportunities")
def top_opportunities(limit: int = 10, db: Session = Depends(get_db)):
    opportunities = (
        db.query(Opportunity)
        .order_by(Opportunity.opportunity_score.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": o.id,
            "description": o.description,
            "score": o.opportunity_score,
            "urgency": o.urgency,
            "status": o.status,
            "country_code": o.country_code,
            "detected_at": o.detected_at,
        }
        for o in opportunities
    ]
