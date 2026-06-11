from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.pricing import CommercialWorkflowRequest, CommercialWorkflowResponse
from app.services.order_workflow import OrderWorkflowService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/from-message", response_model=CommercialWorkflowResponse)
def create_order_from_message(
    request: CommercialWorkflowRequest,
    db: Session = Depends(get_db),
) -> CommercialWorkflowResponse:
    try:
        service = OrderWorkflowService(db)
        return service.process_message_to_document(request)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
