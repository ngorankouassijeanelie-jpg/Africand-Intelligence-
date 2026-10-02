import re

from app.modules.ai.base import AIProvider, ExtractionContext, ExtractionResult

AMOUNT_PATTERN = re.compile(
    r"(?P<value>\d[\d\s.,]*)\s*(?P<scale>milliards?|millions?|mds?|m)\s*(?P<currency>FCFA|XOF|EUR|USD|\$|€)?",
    re.IGNORECASE,
)

URGENCY_HIGH_KEYWORDS = ["urgent", "immédiat", "immediate", "ce mois", "deadline proche"]
CURRENCY_MAP = {"fcfa": "XOF", "xof": "XOF", "eur": "EUR", "€": "EUR", "usd": "USD", "$": "USD"}


class MockAIProvider(AIProvider):
    """Extraction par regles (mots-cles + regex), sans dependance a un LLM externe.

    Sert de moteur par defaut (fonctionne sans cle API) et de filet de secours
    si un fournisseur LLM externe est indisponible. Ne produit jamais de champ
    qui n'est pas directement appuye par le texte source.
    """

    name = "mock"

    def extract(self, text: str, title: str, context: ExtractionContext) -> ExtractionResult:
        full_text = f"{title}\n{text}".lower()

        matched_triggers = []
        suggested_services: list[str] = []
        for trig in context.trigger_catalog:
            keywords = [k.lower() for k in trig.get("keywords", [])]
            if any(kw in full_text for kw in keywords):
                matched_triggers.append(trig["code"])
                suggested_services.extend(trig.get("potential_services", []))

        country_code = None
        for country in context.country_catalog:
            if country["name"].lower() in full_text:
                country_code = country["code"]
                break

        sector_id = None
        for sector in context.sector_catalog:
            if sector["name"].lower() in full_text:
                sector_id = sector["id"]
                break

        amount, currency = self._extract_amount(full_text)

        urgency = "high" if any(k in full_text for k in URGENCY_HIGH_KEYWORDS) else "medium"
        if amount and amount >= 10_000_000_000:
            urgency = "high"

        company_name = self._guess_company_name(title)

        confidence = 0.35
        if matched_triggers:
            confidence += 0.25
        if company_name:
            confidence += 0.15
        if amount:
            confidence += 0.1
        if country_code:
            confidence += 0.1
        confidence = min(confidence, 0.9)  # un moteur par mots-cles ne depasse jamais 0.9

        return ExtractionResult(
            matched_trigger_codes=matched_triggers,
            company_name=company_name,
            country_code=country_code,
            sector_id=sector_id,
            amount=amount,
            currency=currency,
            urgency=urgency,
            suggested_service=list(dict.fromkeys(suggested_services)),
            summary=title,
            decision_maker=None,
            confidence=round(confidence, 2),
        )

    @staticmethod
    def _extract_amount(text: str) -> tuple[float | None, str | None]:
        match = AMOUNT_PATTERN.search(text)
        if not match:
            return None, None
        raw_value = match.group("value").replace(" ", "").replace(",", ".")
        try:
            value = float(raw_value)
        except ValueError:
            return None, None
        scale = match.group("scale").lower()
        if scale.startswith("milliard") or scale == "mds" or scale == "md":
            value *= 1_000_000_000
        else:
            value *= 1_000_000
        currency_raw = (match.group("currency") or "fcfa").lower()
        currency = CURRENCY_MAP.get(currency_raw, "XOF")
        return value, currency

    @staticmethod
    def _guess_company_name(title: str) -> str | None:
        # Heuristique simple : premiere sequence de mots capitalises (>=2 lettres)
        # au debut du titre, typique d'un nom d'entreprise dans un communique.
        match = re.match(r"^((?:[A-Z][\w&.\-]*\s?){1,4})", title.strip())
        if not match:
            return None
        candidate = match.group(1).strip()
        if len(candidate) < 3 or candidate.lower() in {"le", "la", "les", "un", "une"}:
            return None
        return candidate
