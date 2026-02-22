from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    shop_name = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="vendor_profile")
    market = relationship("Market", back_populates="vendor_profiles")


class PriceEntry(Base):
    __tablename__ = "price_entries"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    entry_date = Column(Date, nullable=False, server_default=func.current_date())
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.pending)
    admin_note = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vendor_user = relationship("User", back_populates="price_submissions", foreign_keys=[vendor_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    product = relationship("Product", back_populates="price_entries")
    market = relationship("Market", back_populates="price_entries")
