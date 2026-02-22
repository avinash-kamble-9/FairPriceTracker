from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Numeric, text
from datetime import date, timedelta
from typing import List, Optional
from app.models.price_entry import PriceEntry, ApprovalStatus
from app.models.market import Market, Product
from app.schemas.schemas import MarketStats, PriceTrend, ProductAnalytics


SPIKE_THRESHOLD = 0.20  # 20% above 7-day moving average


def get_product_market_stats_today(db: Session, product_id: int, market_id: int) -> dict:
    today = date.today()
    row = (
        db.query(
            func.avg(PriceEntry.price_per_unit).label("avg"),
            func.min(PriceEntry.price_per_unit).label("min"),
            func.max(PriceEntry.price_per_unit).label("max"),
            func.count(PriceEntry.id).label("count"),
        )
        .filter(
            PriceEntry.product_id == product_id,
            PriceEntry.market_id == market_id,
            PriceEntry.status == ApprovalStatus.approved,
            PriceEntry.entry_date == today,
        )
        .one()
    )
    return {
        "avg": float(row.avg) if row.avg else None,
        "min": float(row.min) if row.min else None,
        "max": float(row.max) if row.max else None,
        "count": row.count,
    }


def get_7day_moving_average(db: Session, product_id: int, market_id: int) -> Optional[float]:
    today = date.today()
    since = today - timedelta(days=7)
    row = (
        db.query(func.avg(PriceEntry.price_per_unit))
        .filter(
            PriceEntry.product_id == product_id,
            PriceEntry.market_id == market_id,
            PriceEntry.status == ApprovalStatus.approved,
            PriceEntry.entry_date >= since,
            PriceEntry.entry_date < today,
        )
        .scalar()
    )
    return float(row) if row else None


def get_trend_30d(db: Session, product_id: int, market_id: int) -> List[PriceTrend]:
    today = date.today()
    since = today - timedelta(days=30)
    rows = (
        db.query(
            PriceEntry.entry_date,
            func.avg(PriceEntry.price_per_unit).label("avg"),
            func.min(PriceEntry.price_per_unit).label("min"),
            func.max(PriceEntry.price_per_unit).label("max"),
            func.count(PriceEntry.id).label("count"),
        )
        .filter(
            PriceEntry.product_id == product_id,
            PriceEntry.market_id == market_id,
            PriceEntry.status == ApprovalStatus.approved,
            PriceEntry.entry_date >= since,
        )
        .group_by(PriceEntry.entry_date)
        .order_by(PriceEntry.entry_date)
        .all()
    )
    return [
        PriceTrend(
            entry_date=r.entry_date,
            avg_price=float(r.avg),
            min_price=float(r.min),
            max_price=float(r.max),
            vendor_count=r.count,
        )
        for r in rows
    ]


def get_product_analytics(db: Session, product_id: int, market_id: int) -> ProductAnalytics:
    product = db.query(Product).filter(Product.id == product_id).first()
    today_stats = get_product_market_stats_today(db, product_id, market_id)
    moving_avg = get_7day_moving_average(db, product_id, market_id)
    trend = get_trend_30d(db, product_id, market_id)

    today_avg = today_stats["avg"]
    spike = False
    if today_avg and moving_avg:
        spike = today_avg > moving_avg * (1 + SPIKE_THRESHOLD)

    return ProductAnalytics(
        product_id=product_id,
        product_name=product.name if product else "Unknown",
        unit=product.unit if product else "kg",
        today_avg=today_avg,
        today_min=today_stats["min"],
        today_max=today_stats["max"],
        vendor_count=today_stats["count"],
        moving_avg_7d=moving_avg,
        spike_alert=spike,
        trend_30d=trend,
    )


def get_all_markets_stats_for_product(db: Session, product_id: int, city_id: Optional[int] = None) -> List[MarketStats]:
    today = date.today()
    seven_days_ago = today - timedelta(days=7)

    q = db.query(Market)
    if city_id:
        q = q.filter(Market.city_id == city_id)
    markets = q.filter(Market.is_active == True).all()

    result = []
    for market in markets:
        stats = get_product_market_stats_today(db, product_id, market.id)
        moving_avg = get_7day_moving_average(db, product_id, market.id)
        spike = False
        if stats["avg"] and moving_avg:
            spike = stats["avg"] > moving_avg * (1 + SPIKE_THRESHOLD)

        result.append(MarketStats(
            market_id=market.id,
            market_name=market.name,
            area=market.area,
            avg_price=stats["avg"],
            min_price=stats["min"],
            max_price=stats["max"],
            vendor_count=stats["count"],
            spike_alert=spike,
        ))
    return result


def get_most_fluctuating_products(db: Session, city_id: Optional[int] = None, limit: int = 5):
    """Products with highest standard deviation in last 30 days"""
    since = date.today() - timedelta(days=30)
    q = (
        db.query(
            PriceEntry.product_id,
            Product.name.label("product_name"),
            func.stddev(PriceEntry.price_per_unit).label("stddev"),
            func.avg(PriceEntry.price_per_unit).label("avg_price"),
        )
        .join(Product, PriceEntry.product_id == Product.id)
        .filter(
            PriceEntry.status == ApprovalStatus.approved,
            PriceEntry.entry_date >= since,
        )
        .group_by(PriceEntry.product_id, Product.name)
        .order_by(func.stddev(PriceEntry.price_per_unit).desc())
        .limit(limit)
    )
    if city_id:
        q = q.join(Market, PriceEntry.market_id == Market.id).filter(Market.city_id == city_id)
    rows = q.all()
    return [{"product_id": r.product_id, "product_name": r.product_name,
             "stddev": float(r.stddev or 0), "avg_price": float(r.avg_price or 0)} for r in rows]
