import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers import admin, alerts, companies, countries, crm, dashboard, investors, opportunities, partners, reports, tenders

logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="Africand Intelligence API",
    description="Africa Opportunity & Investment Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


app.include_router(dashboard.router)
app.include_router(companies.router)
app.include_router(opportunities.router)
app.include_router(tenders.router)
app.include_router(investors.router)
app.include_router(partners.router)
app.include_router(crm.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(countries.router)
app.include_router(admin.router)
