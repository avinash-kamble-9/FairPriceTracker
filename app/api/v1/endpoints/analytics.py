from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.schemas import ProductAnalytics, MarketStats
from app.services import analytics_service
from app.core.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/product/{product_id}/market/{market_id}", response_model=ProductAnalytics)
def product_market_analytics(
    product_id: int,
    market_id: int,
    db: Session = Depends(get_db),
):
    """Full analytics: today's price, 7-day moving avg, spike alert, 30-day trend"""
    return analytics_service.get_product_analytics(db, product_id, market_id)


@router.get("/product/{product_id}/all-markets", response_model=List[MarketStats])
def all_markets_for_product(
    product_id: int,
    city_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Compare same product across all markets in a city — for farmer and consumer dashboards"""
    return analytics_service.get_all_markets_stats_for_product(db, product_id, city_id)


@router.get("/fluctuating-products")
def most_fluctuating(
    city_id: Optional[int] = None,
    limit: int = 5,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Top products by price variance in last 30 days"""
    return analytics_service.get_most_fluctuating_products(db, city_id, limit)
