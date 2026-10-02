from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Alert
from app.schemas.crm import AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if type:
        query = query.filter(Alert.type == type)
    return query.order_by(Alert.sent_at.desc()).limit(200).all()
