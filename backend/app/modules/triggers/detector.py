from sqlalchemy.orm import Session

from app.db.models import TriggerDef


def load_active_triggers(db: Session) -> list[TriggerDef]:
    return db.query(TriggerDef).filter(TriggerDef.active.is_(True)).all()


def trigger_catalog_payload(triggers: list[TriggerDef]) -> list[dict]:
    """Format compact transmis au moteur IA, pour contraindre ses choix de triggers."""
    return [
        {
            "code": t.code,
            "name": t.name,
            "keywords": t.keywords,
            "potential_services": t.potential_services,
        }
        for t in triggers
    ]
