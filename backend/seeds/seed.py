"""Peuple la base avec les referentiels de depart du MVP (section 29 du cahier des charges) :
4 pays prioritaires, secteurs, 10 triggers, sources a curer, et quelques donnees de
demonstration clairement identifiees comme telles pour illustrer le dashboard sur une
base vide.

Usage : python -m seeds.seed
"""

from datetime import date, datetime, timedelta

from app.core.database import Base, SessionLocal, engine
from app.db.models import (
    Alert,
    Company,
    Country,
    CrmDeal,
    Investor,
    Opportunity,
    Partner,
    ScoringWeight,
    Sector,
    Source,
    Tender,
    TriggerDef,
)
from app.modules.scoring.engine import DEFAULT_WEIGHTS

COUNTRIES = [
    # (code, name, phase, active)
    ("CI", "Côte d'Ivoire", 1, True),
    ("SN", "Sénégal", 1, True),
    ("BJ", "Bénin", 1, True),
    ("TG", "Togo", 1, True),
    ("BF", "Burkina Faso", 2, False),
    ("ML", "Mali", 2, False),
    ("NE", "Niger", 2, False),
    ("GW", "Guinée-Bissau", 2, False),
    ("GH", "Ghana", 3, False),
    ("NG", "Nigeria", 3, False),
    ("GN", "Guinée", 3, False),
    ("SL", "Sierra Leone", 3, False),
    ("LR", "Liberia", 3, False),
]

SECTORS = [
    # (name, priority)
    ("Agro-industrie", 1),
    ("Finance / Banques / Assurance", 1),
    ("Énergie", 1),
    ("Infrastructures", 1),
    ("Industrie / Manufacturing", 1),
    ("Télécommunications", 2),
    ("Technologie", 2),
    ("FMCG / Grande consommation", 2),
    ("Logistique", 2),
    ("Transport", 2),
    ("Immobilier", 2),
    ("Mines", 2),
    ("Santé", 2),
    ("Éducation", 2),
    ("Tourisme", 2),
]

TRIGGERS = [
    dict(
        code="fundraising",
        name="Levée de fonds",
        description="Série A/B, financement, dette, equity, capital injection, fundraising",
        keywords=["série a", "série b", "levée de fonds", "financement", "dette", "equity",
                   "capital injection", "fundraising", "levee de fonds"],
        potential_services=["Fundraising advisory", "Financial modelling", "Investment readiness", "Strategic advisory"],
        base_need_score=85,
    ),
    dict(
        code="acquisition",
        name="Acquisition",
        description="Acquisition, rachat, prise de participation, merger, M&A",
        keywords=["acquisition", "rachat", "prise de participation", "merger", "m&a", "fusion"],
        potential_services=["M&A advisory", "Due diligence", "Strategic advisory", "Valuation"],
        base_need_score=82,
    ),
    dict(
        code="expansion",
        name="Expansion",
        description="Nouvelle implantation, expansion régionale, nouveau pays, nouvelle filiale, usine, bureau",
        keywords=["nouvelle implantation", "expansion régionale", "nouveau pays", "nouvelle filiale",
                   "nouvelle usine", "nouveau bureau", "expansion"],
        potential_services=["Market entry", "Strategy", "Market intelligence", "Business development"],
        base_need_score=72,
    ),
    dict(
        code="new_project",
        name="Nouveau projet",
        description="Projet industriel, infrastructure, centrale, usine, plateforme, programme d'investissement",
        keywords=["projet industriel", "infrastructure", "centrale", "usine", "plateforme",
                   "programme d'investissement", "nouvelle unité"],
        potential_services=["Strategy", "Financing", "Investment advisory", "Partnership structuring"],
        base_need_score=75,
    ),
    dict(
        code="joint_venture",
        name="Joint Venture",
        description="Joint venture, partenariat stratégique, consortium, alliance, co-investissement",
        keywords=["joint venture", "partenariat stratégique", "consortium", "alliance", "co-investissement"],
        potential_services=["Strategic partnership", "Market access", "Transaction advisory"],
        base_need_score=74,
    ),
    dict(
        code="tender",
        name="Appel d'offres",
        description="Appel d'offres, consultation, expression of interest, RFP, RFQ, procurement",
        keywords=["appel d'offres", "consultation", "expression of interest", "rfp", "rfq",
                   "procurement", "demande de propositions"],
        potential_services=["Réponse à appel d'offres", "Partenariat de soumission"],
        base_need_score=60,
    ),
    dict(
        code="market_entry",
        name="Entrée sur un nouveau marché",
        description="Entreprise annonçant son entrée sur un nouveau marché ou en Afrique de l'Ouest",
        keywords=["enters côte d'ivoire", "enters west africa", "expands into west africa",
                   "entrée sur le marché", "s'implante en"],
        potential_services=["Market Entry Advisory"],
        base_need_score=78,
    ),
    dict(
        code="financial_distress",
        name="Difficulté financière",
        description="Restructuring, financial distress, debt restructuring, refinancing, liquidation, recapitalisation",
        keywords=["restructuring", "financial distress", "debt restructuring", "refinancing",
                   "liquidation", "recapitalisation", "restructuration"],
        potential_services=["Strategic restructuring", "Financial advisory", "Investor search"],
        base_need_score=70,
    ),
    dict(
        code="major_contract",
        name="Contrat majeur",
        description="Contrat majeur, concession, PPP, government contract, long-term contract, strategic agreement",
        keywords=["contrat majeur", "concession", "ppp", "government contract", "long-term contract",
                   "strategic agreement", "accord stratégique"],
        potential_services=["Expansion", "Financing", "Strategic advisory"],
        base_need_score=76,
    ),
    dict(
        code="active_investor",
        name="Investisseur actif",
        description="Private equity, venture capital, family office, development finance, investor looking for opportunities",
        keywords=["private equity", "venture capital", "family office", "development finance",
                   "investment fund", "investor looking for opportunities"],
        potential_services=["Deal sourcing", "Investment advisory", "Market intelligence"],
        base_need_score=65,
    ),
]

# Liste de depart a curer par l'equipe Africand (section 8 / AFRICAND TENDER RADAR).
# Desactivees par defaut : chaque flux doit etre verifie avant activation en production.
SOURCES = [
    ("Jeune Afrique", "https://www.jeuneafrique.com/feed/", None, "media", 80),
    ("Financial Afrik", "https://www.financialafrik.com/feed/", None, "media", 78),
    ("Agence Ecofin", "https://www.agenceecofin.com/rss", None, "media", 78),
    ("APA News", "https://apanews.net/feed/", None, "media", 70),
    ("Sika Finance", "https://www.sikafinance.com/rss.xml", "CI", "media", 72),
    ("Abidjan.net Economie", "https://news.abidjan.net/emission/economie.rss", "CI", "media", 65),
    ("La Tribune Afrique", "https://afrique.latribune.fr/rss", None, "media", 75),
    ("Les Afriques", "https://www.lesafriques.com/feed", None, "media", 68),
    ("Senego Economie", "https://senego.com/feed", "SN", "media", 60),
    ("Republicoftogo", "https://republicoftogo.com/feed/", "TG", "media", 60),
    ("BOAD - Communiqués", "https://www.boad.org", None, "institution", 85),
    ("BCEAO - Publications", "https://www.bceao.int", None, "institution", 85),
    ("UEMOA - Actualités", "https://www.uemoa.int", None, "institution", 82),
    ("CEPICI (Agence de promotion des investissements CI)", "https://www.cepici.ci", "CI", "institution", 80),
    ("APIX Sénégal", "https://www.apix.sn", "SN", "institution", 80),
    ("Banque Mondiale - Appels d'offres Afrique de l'Ouest", "https://www.banquemondiale.org", None, "tender", 85),
    ("BAD - Appels d'offres", "https://www.afdb.org", None, "tender", 85),
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Country).first():
            for code, name, phase, active in COUNTRIES:
                db.add(Country(code=code, name=name, phase=phase, active=active))

        if not db.query(Sector).first():
            for name, priority in SECTORS:
                db.add(Sector(name=name, priority=priority, active=True))

        if not db.query(TriggerDef).first():
            for trig in TRIGGERS:
                db.add(TriggerDef(**trig, active=True))

        if not db.query(Source).first():
            for name, url, country_code, category, reliability in SOURCES:
                db.add(
                    Source(
                        name=name,
                        url=url,
                        country_code=country_code,
                        category=category,
                        reliability_score=reliability,
                        active=False,  # a activer depuis l'admin apres verification du flux
                    )
                )

        if not db.query(ScoringWeight).first():
            for criterion, (percent, label) in DEFAULT_WEIGHTS.items():
                db.add(ScoringWeight(criterion=criterion, weight_percent=percent, label=label))

        db.commit()
        _seed_demo_data(db)
        print("Seed terminé.")
    finally:
        db.close()


def _seed_demo_data(db) -> None:
    """Quelques enregistrements de démonstration (préfixés [DÉMO]) pour ne pas
    présenter un dashboard vide au premier lancement. A supprimer une fois que
    le pipeline d'ingestion réel alimente la base."""
    if db.query(Company).filter(Company.name.like("[DÉMO]%")).first():
        return

    sector_agro = db.query(Sector).filter(Sector.name == "Agro-industrie").first()
    sector_finance = db.query(Sector).filter(Sector.name == "Finance / Banques / Assurance").first()
    trigger_new_project = db.query(TriggerDef).filter(TriggerDef.code == "new_project").first()
    trigger_fundraising = db.query(TriggerDef).filter(TriggerDef.code == "fundraising").first()

    company = Company(
        name="[DÉMO] XYZ Agro Group",
        country_code="CI",
        sector_id=sector_agro.id if sector_agro else None,
        description="Donnée de démonstration — société fictive illustrant une fiche entreprise.",
    )
    db.add(company)
    db.flush()

    opp1 = Opportunity(
        company_id=company.id,
        trigger_id=trigger_new_project.id if trigger_new_project else None,
        description="[DÉMO] XYZ Agro Group annonce un investissement de 15 Mds FCFA dans une nouvelle unité de transformation.",
        country_code="CI",
        sector_id=sector_agro.id if sector_agro else None,
        amount=15_000_000_000,
        currency="XOF",
        source_url="https://example.com/demo-source-1",
        opportunity_score=88,
        score_breakdown={"note": "donnée de démonstration, non issue du pipeline réel"},
        urgency="high",
        suggested_service=["Strategy", "Financing"],
        confidence=1.0,
        status="detected",
    )
    opp2 = Opportunity(
        company_id=None,
        trigger_id=trigger_fundraising.id if trigger_fundraising else None,
        description="[DÉMO] Une fintech sénégalaise boucle une série A de 4 Mds FCFA.",
        country_code="SN",
        sector_id=sector_finance.id if sector_finance else None,
        amount=4_000_000_000,
        currency="XOF",
        source_url="https://example.com/demo-source-2",
        opportunity_score=79,
        score_breakdown={"note": "donnée de démonstration, non issue du pipeline réel"},
        urgency="medium",
        suggested_service=["Fundraising advisory", "Investment readiness"],
        confidence=1.0,
        status="qualified",
    )
    db.add_all([opp1, opp2])
    db.flush()

    db.add(
        Alert(
            opportunity_id=opp1.id,
            type="priority",
            channel="dashboard",
            recipient="equipe-africand",
            message=f"[DÉMO] PRIORITÉ IMMÉDIATE — {opp1.description} (score {opp1.opportunity_score}/100)",
            status="sent",
        )
    )

    db.add(
        CrmDeal(
            opportunity_id=opp2.id,
            stage="qualified",
            estimated_value=50_000_000,
            probability=30,
            expected_close=date.today() + timedelta(days=45),
            owner="Managing Partner",
            next_action="Planifier un premier contact avec les fondateurs",
        )
    )

    db.add(
        Tender(
            institution="[DÉMO] BOAD",
            country_code="CI",
            sector_id=sector_finance.id if sector_finance else None,
            title="Mission d'assistance technique — stratégie régionale",
            description="Donnée de démonstration illustrant l'Africand Tender Radar.",
            budget="Non communiqué",
            deadline=date.today() + timedelta(days=30),
            source_url="https://example.com/demo-tender",
            fit_score=91,
            status="open",
        )
    )

    db.add(
        Investor(
            name="[DÉMO] West Africa Growth Fund",
            type="Private Equity",
            countries=["CI", "SN"],
            sectors=["Agro-industrie", "Industrie / Manufacturing"],
            ticket_size="1-10 M USD",
            recent_activity="Donnée de démonstration.",
        )
    )

    db.add(
        Partner(
            name="[DÉMO] Cabinet Juridique Partenaire",
            category="Cabinet juridique",
            countries=["CI"],
            sectors=["Finance / Banques / Assurance"],
            description="Donnée de démonstration illustrant l'Africand Partner Radar.",
        )
    )

    db.commit()


if __name__ == "__main__":
    seed()
