from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Company, Opportunity, Sector, Tender, TriggerDef

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily-brief")
def daily_brief(db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=1)
    opportunities = (
        db.query(Opportunity)
        .filter(Opportunity.detected_at >= since)
        .order_by(Opportunity.opportunity_score.desc())
        .all()
    )
    return {
        "titre": "Daily Opportunity Brief",
        "periode": f"{since.date()} - {datetime.utcnow().date()}",
        "total_opportunites": len(opportunities),
        "opportunites": [
            {
                "id": o.id,
                "description": o.description,
                "score": o.opportunity_score,
                "urgence": o.urgency,
                "pays": o.country_code,
            }
            for o in opportunities
        ],
    }


@router.get("/weekly")
def weekly_report(db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=7)
    opportunities = db.query(Opportunity).filter(Opportunity.detected_at >= since).all()
    tenders = db.query(Tender).filter(Tender.detected_at >= since).all()

    sector_counter = Counter(o.sector_id for o in opportunities if o.sector_id)
    trigger_counter = Counter(o.trigger_id for o in opportunities if o.trigger_id)

    top_sectors = []
    for sector_id, count in sector_counter.most_common(5):
        sector = db.get(Sector, sector_id)
        top_sectors.append({"sector": sector.name if sector else "N/A", "count": count})

    top_triggers = []
    for trigger_id, count in trigger_counter.most_common(5):
        trigger = db.get(TriggerDef, trigger_id)
        top_triggers.append({"trigger": trigger.name if trigger else "N/A", "count": count})

    top_opportunities = sorted(opportunities, key=lambda o: o.opportunity_score, reverse=True)[:10]
    top_companies_ids = Counter(o.company_id for o in opportunities if o.company_id).most_common(5)
    top_companies = []
    for company_id, count in top_companies_ids:
        company = db.get(Company, company_id)
        top_companies.append({"company": company.name if company else "N/A", "opportunity_count": count})

    return {
        "titre": "Weekly Africa Opportunity Report",
        "periode": f"{since.date()} - {datetime.utcnow().date()}",
        "total_opportunites": len(opportunities),
        "total_appels_offres": len(tenders),
        "top_secteurs": top_sectors,
        "top_triggers": top_triggers,
        "top_entreprises": top_companies,
        "top_opportunites": [
            {"id": o.id, "description": o.description, "score": o.opportunity_score} for o in top_opportunities
        ],
    }
