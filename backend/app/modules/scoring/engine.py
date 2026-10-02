from sqlalchemy.orm import Session

from app.db.models import ScoringWeight, Sector, TriggerDef
from app.modules.ai.base import ExtractionResult

DEFAULT_WEIGHTS = {
    "need": (25, "Besoin potentiel"),
    "financial_capacity": (20, "Capacité financière"),
    "fit": (20, "Adéquation avec Africand"),
    "urgency": (15, "Urgence"),
    "deal_size": (10, "Taille potentielle de mission"),
    "decision_maker_access": (10, "Accessibilité du décideur"),
}

URGENCY_SCORES = {"low": 40, "medium": 70, "high": 95}

AMOUNT_TIERS = [
    (50_000_000_000, 100),
    (10_000_000_000, 85),
    (1_000_000_000, 65),
    (100_000_000, 45),
    (0, 25),
]


def ensure_default_weights(db: Session) -> None:
    existing = {w.criterion for w in db.query(ScoringWeight).all()}
    for criterion, (percent, label) in DEFAULT_WEIGHTS.items():
        if criterion not in existing:
            db.add(ScoringWeight(criterion=criterion, weight_percent=percent, label=label))
    db.commit()


def _amount_tier_score(amount: float | None) -> int:
    if not amount:
        return 35
    for threshold, score in AMOUNT_TIERS:
        if amount >= threshold:
            return score
    return 25


def score_opportunity(
    db: Session,
    extraction: ExtractionResult,
    trigger: TriggerDef | None,
    sector: Sector | None,
) -> tuple[int, dict]:
    """Calcule le score d'opportunite (0-100) et le detail des sous-scores.

    Ponderations recuperees depuis la table scoring_weights (modifiables en admin),
    conformement a la section 10 du cahier des charges.
    """
    weights = {w.criterion: w.weight_percent for w in db.query(ScoringWeight).all()}
    if not weights:
        weights = {k: v[0] for k, v in DEFAULT_WEIGHTS.items()}

    need_score = trigger.base_need_score if trigger else 50
    financial_capacity_score = _amount_tier_score(extraction.amount)
    deal_size_score = _amount_tier_score(extraction.amount)

    if sector is None:
        fit_score = 40
    elif sector.priority == 1:
        fit_score = 100
    else:
        fit_score = 70

    urgency_score = URGENCY_SCORES.get(extraction.urgency, 60)
    decision_maker_access_score = 80 if extraction.decision_maker else 30

    sub_scores = {
        "need": need_score,
        "financial_capacity": financial_capacity_score,
        "fit": fit_score,
        "urgency": urgency_score,
        "deal_size": deal_size_score,
        "decision_maker_access": decision_maker_access_score,
    }

    total_weight = sum(weights.get(k, 0) for k in sub_scores) or 100
    weighted_sum = sum(sub_scores[k] * weights.get(k, DEFAULT_WEIGHTS[k][0]) for k in sub_scores)
    final_score = round(weighted_sum / total_weight)
    final_score = max(0, min(100, final_score))

    breakdown = {
        "sub_scores": sub_scores,
        "weights": weights,
        "confidence": extraction.confidence,
    }
    return final_score, breakdown


def score_tender_fit(sector: Sector | None, country_active: bool, has_budget: bool) -> int:
    """Tender Fit Score : adequation d'un appel d'offres avec le profil Africand."""
    score = 40
    if sector is not None:
        score += 35 if sector.priority == 1 else 20
    if country_active:
        score += 15
    if has_budget:
        score += 10
    return max(0, min(100, score))


def priority_bucket(score: int) -> str:
    if score >= 90:
        return "PRIORITÉ IMMÉDIATE"
    if score >= 75:
        return "HIGH PRIORITY"
    if score >= 50:
        return "NURTURE"
    return "MONITOR"


def recommended_action(score: int) -> str:
    if score >= 90:
        return "Contacter rapidement le décideur"
    if score >= 75:
        return "Prise de contact sous 7 jours"
    if score >= 50:
        return "Suivre et développer la relation"
    return "Surveillance uniquement"
