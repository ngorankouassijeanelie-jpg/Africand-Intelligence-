# AFRICAND INTELLIGENCE

**Africa Opportunity & Investment Intelligence Platform**
Projet : Africand Consulting · Zone prioritaire : Afrique de l'Ouest / UEMOA

> Transformer automatiquement les informations publiques disponibles en opportunités
> commerciales qualifiées pour Africand : détecter l'événement → l'entreprise → le
> besoin probable → le décideur → le service Africand → le score → l'action commerciale
> recommandée.

Ce dépôt contient le **MVP** décrit dans le cahier des charges (périmètre : Côte d'Ivoire,
Sénégal, Bénin, Togo · 10 triggers · scoring configurable · dashboard, CRM, alertes,
Tender Radar).

## Architecture

```
SOURCES (RSS, institutions, appels d'offres)
   → DATA COLLECTION (collectors)
   → AI ENGINE (extraction structurée, multi-fournisseurs)
   → TRIGGER DETECTION
   → DEDUPLICATION (normalization)
   → OPPORTUNITY SCORING
   → OPPORTUNITIES / CRM / ALERTS
   → DASHBOARD
```

Le code est organisé en modules indépendants, conformément à la section 23 du cahier
des charges :

```
backend/app/
  core/            configuration, base de données, sécurité
  db/models.py     modèle de données (section 24)
  modules/
    ai/            moteur IA agnostique du fournisseur (mock / OpenAI / Anthropic)
    triggers/      catalogue et détection des triggers métier
    scoring/        moteur de scoring pondéré (section 10)
    normalization/ déduplication des événements multi-sources
    collectors/    collecteurs de données (RSS pour le MVP)
    pipeline.py    orchestration collecte → IA → triggers → dedup → scoring → alertes
  routers/         API FastAPI (companies, opportunities, tenders, crm, alerts, admin...)
backend/seeds/     référentiels de départ (pays, secteurs, triggers, sources, démo)
frontend/          interface Next.js (français), dashboard premium
```

## Principes clés respectés

- **Anti-hallucination** : "No source = No fact". Le moteur IA ne produit que des
  champs directement appuyés par le texte source ; toute opportunité conserve sa
  source d'origine, son URL et un niveau de confiance.
- **Multi-fournisseur IA** : `AI_PROVIDER=mock|openai|anthropic` dans `.env` — aucun
  changement de code métier nécessaire pour changer de LLM.
- **Déduplication** : plusieurs sources relayant le même événement sont regroupées
  sur une seule opportunité (`related_sources`).
- **Scoring configurable** : pondérations modifiables depuis Administration sans
  toucher au code (besoin, capacité financière, adéquation, urgence, taille de
  mission, accessibilité du décideur).
- **Administration sans code** : sources, secteurs, triggers et pondérations sont
  gérés depuis l'interface Admin.

## Démarrage rapide (développement local)

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m seeds.seed        # peuple pays, secteurs, triggers, sources, démo
uvicorn app.main:app --reload
```

API disponible sur http://localhost:8000 (doc interactive sur `/docs`).
Identifiants admin par défaut : `admin@africand.com` / valeur de `ADMIN_PASSWORD` dans `.env`.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Interface disponible sur http://localhost:3000.

### Avec Docker Compose (Postgres + backend + frontend)

```bash
docker compose up --build
```

## Lancer une collecte

Les sources fournies dans le seed sont **désactivées par défaut** (à vérifier et
activer depuis Administration → Sources, une fois les flux RSS confirmés). Une fois
des sources actives, lancez la collecte depuis Administration → "Lancer la collecte",
ou via l'API :

```bash
curl -X POST http://localhost:8000/admin/ingest/run \
  -H "Authorization: Bearer <token obtenu via /admin/login>"
```

Le pipeline : collecte RSS → extraction IA (triggers, entreprise, montant, pays,
secteur, urgence) → déduplication → scoring → création d'alertes si score ≥ 75.

## Roadmap (au-delà du MVP)

Voir le cahier des charges complet pour les phases 2/3 (extension géographique),
AFRICAND INTELLIGENCE 2.0 (prédiction des besoins, corporate mapping, deal sourcing
avancé, M&A radar) et l'intégration Supabase Auth / stockage vectoriel pour la
recherche sémantique.
