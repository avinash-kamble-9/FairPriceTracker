from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.market import City, Market, Product, ProductCategory
from app.schemas.schemas import (
    CityCreate, CityOut, MarketCreate, MarketOut,
    ProductCreate, ProductOut, CategoryCreate, CategoryOut
)
from app.core.security import get_current_user, require_role

router = APIRouter(tags=["Markets & Products"])


# ─── Cities ──────────────────────────────────────────────────────────────────

@router.get("/cities", response_model=List[CityOut])
def list_cities(db: Session = Depends(get_db)):
    return db.query(City).filter(City.is_active == True).all()


@router.post("/cities", response_model=CityOut, status_code=201)
def create_city(
    payload: CityCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    city = City(**payload.dict())
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


# ─── Markets ─────────────────────────────────────────────────────────────────

@router.get("/markets", response_model=List[MarketOut])
def list_markets(city_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Market).filter(Market.is_active == True)
    if city_id:
        q = q.filter(Market.city_id == city_id)
    return q.all()


@router.get("/markets/{market_id}", response_model=MarketOut)
def get_market(market_id: int, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.post("/markets", response_model=MarketOut, status_code=201)
def create_market(
    payload: MarketCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    market = Market(**payload.dict())
    db.add(market)
    db.commit()
    db.refresh(market)
    return market


# ─── Categories ──────────────────────────────────────────────────────────────

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(ProductCategory).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    cat = ProductCategory(**payload.dict())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ─── Products ────────────────────────────────────────────────────────────────

@router.get("/products", response_model=List[ProductOut])
def list_products(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Product).filter(Product.is_active == True)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    return q.all()


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
