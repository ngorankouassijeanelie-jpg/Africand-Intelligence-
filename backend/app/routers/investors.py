from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Investor
from app.schemas.tenders import InvestorIn, InvestorOut

router = APIRouter(prefix="/investors", tags=["investors"])


@router.get("", response_model=list[InvestorOut])
def list_investors(db: Session = Depends(get_db)):
    return db.query(Investor).order_by(Investor.name).all()


@router.post("", response_model=InvestorOut)
def create_investor(payload: InvestorIn, db: Session = Depends(get_db)):
    investor = Investor(**payload.model_dump())
    db.add(investor)
    db.commit()
    db.refresh(investor)
    return investor


@router.get("/{investor_id}", response_model=InvestorOut)
def get_investor(investor_id: int, db: Session = Depends(get_db)):
    investor = db.get(Investor, investor_id)
    if not investor:
        raise HTTPException(status_code=404, detail="Investisseur introuvable")
    return investor
