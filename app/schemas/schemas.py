from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────────────

class UserRoleEnum(str, Enum):
    farmer = "farmer"
    consumer = "consumer"
    vendor = "vendor"
    admin = "admin"


class ApprovalStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: UserRoleEnum = UserRoleEnum.consumer


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    full_name: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    role: UserRoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── City ────────────────────────────────────────────────────────────────────

class CityCreate(BaseModel):
    name: str
    state: str


class CityOut(BaseModel):
    id: int
    name: str
    state: str
    is_active: bool

    class Config:
        from_attributes = True


# ─── Market ──────────────────────────────────────────────────────────────────

class MarketCreate(BaseModel):
    name: str
    area: str
    city_id: int
    address: Optional[str] = None


class MarketOut(BaseModel):
    id: int
    name: str
    area: str
    city_id: int
    address: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ─── Product ─────────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    name_marathi: Optional[str] = None
    category_id: int
    unit: str = "kg"


class ProductOut(BaseModel):
    id: int
    name: str
    name_marathi: Optional[str]
    category_id: int
    unit: str
    is_active: bool

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    name_marathi: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    name_marathi: Optional[str]

    class Config:
        from_attributes = True


# ─── Price Entry ─────────────────────────────────────────────────────────────

class PriceEntryCreate(BaseModel):
    product_id: int
    market_id: int
    price_per_unit: Decimal = Field(..., gt=0, le=99999)
    entry_date: Optional[date] = None


class PriceEntryUpdate(BaseModel):
    price_per_unit: Decimal = Field(..., gt=0, le=99999)


class AdminReview(BaseModel):
    status: ApprovalStatusEnum
    admin_note: Optional[str] = None


class PriceEntryOut(BaseModel):
    id: int
    vendor_id: int
    product_id: int
    market_id: int
    price_per_unit: Decimal
    entry_date: date
    status: ApprovalStatusEnum
    admin_note: Optional[str]
    created_at: datetime
    product: Optional[ProductOut]
    market: Optional[MarketOut]

    class Config:
        from_attributes = True


# ─── Analytics ───────────────────────────────────────────────────────────────

class MarketStats(BaseModel):
    market_id: int
    market_name: str
    area: str
    avg_price: Optional[float]
    min_price: Optional[float]
    max_price: Optional[float]
    vendor_count: int
    spike_alert: bool


class PriceTrend(BaseModel):
    entry_date: date
    avg_price: float
    min_price: float
    max_price: float
    vendor_count: int


class ProductAnalytics(BaseModel):
    product_id: int
    product_name: str
    unit: str
    today_avg: Optional[float]
    today_min: Optional[float]
    today_max: Optional[float]
    vendor_count: int
    moving_avg_7d: Optional[float]
    spike_alert: bool
    trend_30d: List[PriceTrend]
