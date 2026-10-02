import hashlib
from difflib import SequenceMatcher
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import Opportunity

SIMILARITY_THRESHOLD = 0.72
DEDUP_WINDOW_DAYS = 10


def content_hash(title: str, url: str) -> str:
    return hashlib.sha256(f"{title.strip().lower()}|{url.strip().lower()}".encode()).hexdigest()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicate_opportunity(
    db: Session,
    description: str,
    company_name: str | None,
    trigger_id: int | None,
) -> Opportunity | None:
    """Recherche une opportunite proche (meme evenement rapporte par plusieurs sources).

    Plusieurs medias peuvent relayer le meme evenement (ex: une levee de fonds
    reprise par Reuters, Jeune Afrique et le communique de l'entreprise) : on
    regroupe les sources au lieu de dupliquer l'opportunite.
    """
    cutoff = datetime.utcnow() - timedelta(days=DEDUP_WINDOW_DAYS)
    candidates = db.query(Opportunity).filter(Opportunity.detected_at >= cutoff)
    if trigger_id is not None:
        candidates = candidates.filter(Opportunity.trigger_id == trigger_id)

    for candidate in candidates.all():
        score = _similarity(description, candidate.description)
        if company_name and candidate.company and company_name.lower() in candidate.company.name.lower():
            score += 0.15
        if score >= SIMILARITY_THRESHOLD:
            return candidate
    return None


def merge_source_into_opportunity(opportunity: Opportunity, source_url: str) -> None:
    if source_url and source_url not in opportunity.related_sources and source_url != opportunity.source_url:
        opportunity.related_sources = [*opportunity.related_sources, source_url]
