from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Numeric, Date
from fastapi import HTTPException
from datetime import date, timedelta
from typing import List, Optional
from app.models.price_entry import PriceEntry, ApprovalStatus
from app.models.market import Market, Product
from app.schemas.schemas import PriceEntryCreate, PriceEntryUpdate, AdminReview


def submit_price(db: Session, payload: PriceEntryCreate, vendor_id: int) -> PriceEntry:
    entry = PriceEntry(
        vendor_id=vendor_id,
        product_id=payload.product_id,
        market_id=payload.market_id,
        price_per_unit=payload.price_per_unit,
        entry_date=payload.entry_date or date.today(),
        status=ApprovalStatus.pending,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_vendor_submissions(db: Session, vendor_id: int) -> List[PriceEntry]:
    return (
        db.query(PriceEntry)
        .filter(PriceEntry.vendor_id == vendor_id)
        .order_by(PriceEntry.created_at.desc())
        .all()
    )


def update_vendor_submission(db: Session, entry_id: int, vendor_id: int, payload: PriceEntryUpdate) -> PriceEntry:
    entry = db.query(PriceEntry).filter(
        PriceEntry.id == entry_id,
        PriceEntry.vendor_id == vendor_id,
        PriceEntry.status == ApprovalStatus.pending,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found or not editable")
    entry.price_per_unit = payload.price_per_unit
    db.commit()
    db.refresh(entry)
    return entry


def admin_review_entry(db: Session, entry_id: int, payload: AdminReview, admin_id: int) -> PriceEntry:
    from datetime import datetime
    entry = db.query(PriceEntry).filter(PriceEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    entry.status = payload.status
    entry.admin_note = payload.admin_note
    entry.reviewed_by = admin_id
    entry.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return entry


def get_all_submissions(
    db: Session,
    product_id: Optional[int] = None,
    market_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    status: Optional[ApprovalStatus] = None,
    entry_date: Optional[date] = None,
) -> List[PriceEntry]:
    q = db.query(PriceEntry)
    if product_id:
        q = q.filter(PriceEntry.product_id == product_id)
    if market_id:
        q = q.filter(PriceEntry.market_id == market_id)
    if vendor_id:
        q = q.filter(PriceEntry.vendor_id == vendor_id)
    if status:
        q = q.filter(PriceEntry.status == status)
    if entry_date:
        q = q.filter(PriceEntry.entry_date == entry_date)
    return q.order_by(PriceEntry.created_at.desc()).all()
