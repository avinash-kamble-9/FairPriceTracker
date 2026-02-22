from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.database import get_db
from app.schemas.schemas import PriceEntryCreate, PriceEntryUpdate, PriceEntryOut, AdminReview, ApprovalStatusEnum
from app.services import price_service
from app.models.price_entry import ApprovalStatus
from app.core.security import get_current_user, require_role

router = APIRouter(tags=["Price Entries"])


# ─── Vendor Routes ───────────────────────────────────────────────────────────

@router.post("/prices", response_model=PriceEntryOut, status_code=201)
def submit_price(
    payload: PriceEntryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("vendor")),
):
    return price_service.submit_price(db, payload, current_user.id)


@router.get("/prices/my-submissions", response_model=List[PriceEntryOut])
def my_submissions(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("vendor")),
):
    return price_service.get_vendor_submissions(db, current_user.id)


@router.patch("/prices/{entry_id}", response_model=PriceEntryOut)
def update_submission(
    entry_id: int,
    payload: PriceEntryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("vendor")),
):
    return price_service.update_vendor_submission(db, entry_id, current_user.id, payload)


# ─── Admin Routes ────────────────────────────────────────────────────────────

@router.get("/admin/prices", response_model=List[PriceEntryOut])
def admin_list_prices(
    product_id: Optional[int] = None,
    market_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    status: Optional[ApprovalStatusEnum] = None,
    entry_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    status_enum = ApprovalStatus(status.value) if status else None
    return price_service.get_all_submissions(
        db, product_id, market_id, vendor_id, status_enum, entry_date
    )


@router.post("/admin/prices/{entry_id}/review", response_model=PriceEntryOut)
def review_price(
    entry_id: int,
    payload: AdminReview,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    return price_service.admin_review_entry(db, entry_id, payload, current_user.id)
