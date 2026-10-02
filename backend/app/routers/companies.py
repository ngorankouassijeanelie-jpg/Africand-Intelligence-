from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Company, Contact, Opportunity
from app.schemas.companies import CompanyDetail, CompanyIn, CompanyOut, ContactIn, ContactOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(
    country_code: str | None = None,
    sector_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Company)
    if country_code:
        query = query.filter(Company.country_code == country_code)
    if sector_id:
        query = query.filter(Company.sector_id == sector_id)
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))
    return query.order_by(Company.updated_at.desc()).limit(200).all()


@router.post("", response_model=CompanyOut)
def create_company(payload: CompanyIn, db: Session = Depends(get_db)):
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyDetail)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")

    contacts = db.query(Contact).filter(Contact.company_id == company_id).all()
    opportunities = db.query(Opportunity).filter(Opportunity.company_id == company_id).all()
    commercial_score = max((o.opportunity_score for o in opportunities), default=0)

    return CompanyDetail(
        **CompanyOut.model_validate(company).model_dump(),
        contacts=[ContactOut.model_validate(c) for c in contacts],
        opportunity_count=len(opportunities),
        commercial_score=commercial_score,
    )


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, payload: CompanyIn, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    for key, value in payload.model_dump().items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.post("/{company_id}/contacts", response_model=ContactOut)
def add_contact(company_id: int, payload: ContactIn, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    contact = Contact(company_id=company_id, **payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact
