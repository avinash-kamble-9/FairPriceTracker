from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g. Mumbai
    state = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    markets = relationship("Market", back_populates="city")


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    area = Column(String(100), nullable=False)  # e.g. Andheri, Dadar
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    city = relationship("City", back_populates="markets")
    price_entries = relationship("PriceEntry", back_populates="market")
    vendor_profiles = relationship("VendorProfile", back_populates="market")


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g. Vegetables, Fruits
    name_marathi = Column(String(100), nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    name_marathi = Column(String(150), nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=False)
    unit = Column(String(30), nullable=False, default="kg")  # kg, dozen, piece
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("ProductCategory", back_populates="products")
    price_entries = relationship("PriceEntry", back_populates="product")
