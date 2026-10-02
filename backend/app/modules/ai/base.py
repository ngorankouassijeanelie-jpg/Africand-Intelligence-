from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class DecisionMaker(BaseModel):
    name: str
    position: str


class ExtractionContext(BaseModel):
    """Referentiels passes au moteur IA pour contraindre l'extraction (anti-hallucination)."""

    trigger_catalog: list[dict] = Field(default_factory=list)  # [{code, name, keywords}]
    country_catalog: list[dict] = Field(default_factory=list)  # [{code, name}]
    sector_catalog: list[dict] = Field(default_factory=list)  # [{id, name}]


class ExtractionResult(BaseModel):
    """Fiche structuree produite a partir d'une information brute.

    Regle fondamentale : "No source = No fact". Tout champ non trouve
    explicitement dans le texte source doit rester vide/None, jamais invente.
    """

    matched_trigger_codes: list[str] = Field(default_factory=list)
    company_name: str | None = None
    country_code: str | None = None
    sector_id: int | None = None
    amount: float | None = None
    currency: str | None = None
    urgency: str = "medium"  # low, medium, high
    suggested_service: list[str] = Field(default_factory=list)
    summary: str = ""
    decision_maker: DecisionMaker | None = None
    confidence: float = 0.5  # 0..1, niveau de confiance de l'extraction


class AIProvider(ABC):
    name: str = "base"

    @abstractmethod
    def extract(self, text: str, title: str, context: ExtractionContext) -> ExtractionResult:
        """Analyse un texte brut et retourne une fiche structuree d'opportunite."""
        raise NotImplementedError
