import logging

from sqlalchemy.orm import Session

from app.db.models import (
    Alert,
    Company,
    Country,
    Opportunity,
    RawItem,
    Sector,
    Source,
    TriggerDef,
)
from app.modules.ai.base import ExtractionContext
from app.modules.ai.engine import extract_opportunity
from app.modules.collectors.rss_collector import RssCollector
from app.modules.normalization.dedup import content_hash, find_duplicate_opportunity, merge_source_into_opportunity
from app.modules.scoring.engine import ensure_default_weights, priority_bucket, score_opportunity
from app.modules.triggers.detector import load_active_triggers, trigger_catalog_payload

logger = logging.getLogger(__name__)

ALERT_THRESHOLD_HIGH = 75
ALERT_THRESHOLD_IMMEDIATE = 90


def _build_context(db: Session) -> tuple[ExtractionContext, dict[str, TriggerDef]]:
    triggers = load_active_triggers(db)
    trigger_by_code = {t.code: t for t in triggers}
    countries = db.query(Country).filter(Country.active.is_(True)).all()
    sectors = db.query(Sector).filter(Sector.active.is_(True)).all()

    context = ExtractionContext(
        trigger_catalog=trigger_catalog_payload(triggers),
        country_catalog=[{"code": c.code, "name": c.name} for c in countries],
        sector_catalog=[{"id": s.id, "name": s.name} for s in sectors],
    )
    return context, trigger_by_code


def _resolve_or_create_company(db: Session, name: str | None, country_code: str | None, sector_id: int | None) -> Company | None:
    if not name:
        return None
    company = (
        db.query(Company)
        .filter(Company.name.ilike(name.strip()))
        .first()
    )
    if company:
        return company
    company = Company(name=name.strip(), country_code=country_code, sector_id=sector_id)
    db.add(company)
    db.flush()
    return company


def collect_raw_items(db: Session) -> int:
    """Collecte depuis toutes les sources actives (module /data/collectors)."""
    sources = db.query(Source).filter(Source.active.is_(True)).all()
    collected_count = 0

    for source in sources:
        collector = RssCollector(source.url)
        items = collector.collect()
        for item in items:
            if not item.url:
                continue
            h = content_hash(item.title, item.url)
            exists = db.query(RawItem).filter(RawItem.content_hash == h).first()
            if exists:
                continue
            raw = RawItem(
                source_id=source.id,
                title=item.title,
                content=item.content,
                url=item.url,
                published_at=item.published_at,
                content_hash=h,
                processed=False,
            )
            db.add(raw)
            collected_count += 1
    db.commit()
    return collected_count


def process_raw_items(db: Session) -> tuple[int, int, int]:
    """Traite les items bruts non traites : IA -> triggers -> dedup -> scoring -> alertes."""
    ensure_default_weights(db)
    context, trigger_by_code = _build_context(db)

    pending_items = db.query(RawItem).filter(RawItem.processed.is_(False)).all()
    created, merged, alerts_sent = 0, 0, 0

    for raw in pending_items:
        extraction = extract_opportunity(raw.content or raw.title, raw.title, context)
        raw.processed = True

        if not extraction.matched_trigger_codes:
            continue

        trigger_code = extraction.matched_trigger_codes[0]
        trigger = trigger_by_code.get(trigger_code)

        duplicate = find_duplicate_opportunity(
            db,
            description=extraction.summary or raw.title,
            company_name=extraction.company_name,
            trigger_id=trigger.id if trigger else None,
        )
        if duplicate:
            merge_source_into_opportunity(duplicate, raw.url)
            db.add(duplicate)
            merged += 1
            continue

        company = _resolve_or_create_company(db, extraction.company_name, extraction.country_code, extraction.sector_id)
        sector = db.get(Sector, extraction.sector_id) if extraction.sector_id else None

        score, breakdown = score_opportunity(db, extraction, trigger, sector)

        opportunity = Opportunity(
            company_id=company.id if company else None,
            trigger_id=trigger.id if trigger else None,
            raw_item_id=raw.id,
            description=extraction.summary or raw.title,
            country_code=extraction.country_code,
            sector_id=extraction.sector_id,
            amount=extraction.amount,
            currency=extraction.currency,
            source_id=raw.source_id,
            source_url=raw.url,
            opportunity_score=score,
            score_breakdown=breakdown,
            urgency=extraction.urgency,
            suggested_service=extraction.suggested_service,
            confidence=extraction.confidence,
            status="detected",
        )
        db.add(opportunity)
        db.flush()
        created += 1

        if extraction.decision_maker and company:
            from app.db.models import Contact

            db.add(
                Contact(
                    company_id=company.id,
                    name=extraction.decision_maker.name,
                    position=extraction.decision_maker.position,
                    source=raw.url,
                )
            )

        if score >= ALERT_THRESHOLD_HIGH:
            alert_type = "priority" if score >= ALERT_THRESHOLD_IMMEDIATE else "high"
            message = (
                f"{priority_bucket(score)} — {opportunity.description[:140]} "
                f"(score {score}/100)"
            )
            db.add(
                Alert(
                    opportunity_id=opportunity.id,
                    type=alert_type,
                    channel="dashboard",
                    recipient="equipe-africand",
                    message=message,
                    status="sent",
                )
            )
            alerts_sent += 1

    db.commit()
    return created, merged, alerts_sent


def run_full_pipeline(db: Session) -> dict:
    collected = collect_raw_items(db)
    created, merged, alerts_sent = process_raw_items(db)
    return {
        "raw_items_collected": collected,
        "opportunities_created": created,
        "opportunities_merged": merged,
        "alerts_sent": alerts_sent,
    }
