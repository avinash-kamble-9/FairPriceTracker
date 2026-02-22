"""
Run this once to seed initial data:
  python seed.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from decimal import Decimal
from app.db.database import SessionLocal, engine, Base
from app.models import user, market, price_entry  # noqa - register models
from app.models.user import User, UserRole
from app.models.market import City, Market, Product, ProductCategory
from app.models.price_entry import PriceEntry, ApprovalStatus, VendorProfile
from app.core.security import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed():
    print("Seeding database...")

    # ── City ──────────────────────────────────────────────────────────────────
    mumbai = City(name="Mumbai", state="Maharashtra")
    db.add(mumbai)
    db.flush()

    # ── Markets ───────────────────────────────────────────────────────────────
    markets = [
        Market(name="Dadar Market", area="Dadar", city_id=mumbai.id, address="Dadar, Mumbai"),
        Market(name="Andheri Market", area="Andheri", city_id=mumbai.id, address="Andheri West, Mumbai"),
        Market(name="Bandra Market", area="Bandra", city_id=mumbai.id, address="Bandra West, Mumbai"),
        Market(name="Borivali Market", area="Borivali", city_id=mumbai.id, address="Borivali East, Mumbai"),
        Market(name="Vasai Market", area="Vasai", city_id=mumbai.id, address="Vasai, Mumbai"),
        Market(name="Navi Mumbai APMC", area="Navi Mumbai", city_id=mumbai.id, address="Vashi, Navi Mumbai"),
    ]
    for m in markets:
        db.add(m)
    db.flush()

    # ── Product Categories ────────────────────────────────────────────────────
    veg_cat = ProductCategory(name="Vegetables", name_marathi="भाजीपाला")
    fruit_cat = ProductCategory(name="Fruits", name_marathi="फळे")
    grain_cat = ProductCategory(name="Grains & Pulses", name_marathi="धान्य")
    db.add_all([veg_cat, fruit_cat, grain_cat])
    db.flush()

    # ── Products ──────────────────────────────────────────────────────────────
    products = [
        Product(name="Tomato", name_marathi="टोमॅटो", category_id=veg_cat.id, unit="kg"),
        Product(name="Onion", name_marathi="कांदा", category_id=veg_cat.id, unit="kg"),
        Product(name="Potato", name_marathi="बटाटा", category_id=veg_cat.id, unit="kg"),
        Product(name="Green Chilli", name_marathi="हिरवी मिरची", category_id=veg_cat.id, unit="kg"),
        Product(name="Banana", name_marathi="केळ", category_id=fruit_cat.id, unit="dozen"),
        Product(name="Mango", name_marathi="आंबा", category_id=fruit_cat.id, unit="kg"),
        Product(name="Rice (Sona Masoori)", name_marathi="तांदूळ", category_id=grain_cat.id, unit="kg"),
        Product(name="Wheat Flour", name_marathi="गहू पीठ", category_id=grain_cat.id, unit="kg"),
    ]
    for p in products:
        db.add(p)
    db.flush()

    # ── Users ─────────────────────────────────────────────────────────────────
    admin = User(
        full_name="Admin User",
        email="admin@fairprice.in",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.admin,
    )
    farmer1 = User(
        full_name="Ramesh Patil",
        email="farmer@fairprice.in",
        hashed_password=get_password_hash("farmer123"),
        role=UserRole.farmer,
    )
    consumer1 = User(
        full_name="Priya Sharma",
        email="consumer@fairprice.in",
        hashed_password=get_password_hash("consumer123"),
        role=UserRole.consumer,
    )
    vendor1 = User(
        full_name="Suresh Vendor",
        email="vendor1@fairprice.in",
        hashed_password=get_password_hash("vendor123"),
        role=UserRole.vendor,
    )
    vendor2 = User(
        full_name="Mahesh Vendor",
        email="vendor2@fairprice.in",
        hashed_password=get_password_hash("vendor123"),
        role=UserRole.vendor,
    )
    db.add_all([admin, farmer1, consumer1, vendor1, vendor2])
    db.flush()

    # ── Vendor Profiles ───────────────────────────────────────────────────────
    db.add(VendorProfile(user_id=vendor1.id, market_id=markets[0].id, shop_name="Suresh Vegetables"))
    db.add(VendorProfile(user_id=vendor2.id, market_id=markets[0].id, shop_name="Mahesh Fresh"))
    db.flush()

    # ── Price Entries (last 30 days, approved) ────────────────────────────────
    import random
    today = date.today()
    base_prices = {
        products[0].id: 40,   # Tomato
        products[1].id: 35,   # Onion
        products[2].id: 30,   # Potato
        products[3].id: 80,   # Green Chilli
        products[4].id: 50,   # Banana
        products[5].id: 120,  # Mango
        products[6].id: 55,   # Rice
        products[7].id: 45,   # Wheat Flour
    }

    for days_ago in range(30, 0, -1):
        entry_date = today - timedelta(days=days_ago)
        for prod_id, base in base_prices.items():
            for vendor_id in [vendor1.id, vendor2.id]:
                for mkt in markets[:3]:  # 3 markets for demo
                    price = Decimal(str(round(base + random.uniform(-base * 0.15, base * 0.15), 2)))
                    entry = PriceEntry(
                        vendor_id=vendor_id,
                        product_id=prod_id,
                        market_id=mkt.id,
                        price_per_unit=price,
                        entry_date=entry_date,
                        status=ApprovalStatus.approved,
                        reviewed_by=admin.id,
                    )
                    db.add(entry)

    # Add some pending entries for today
    for prod in products[:3]:
        entry = PriceEntry(
            vendor_id=vendor1.id,
            product_id=prod.id,
            market_id=markets[0].id,
            price_per_unit=Decimal(str(base_prices[prod.id])),
            entry_date=today,
            status=ApprovalStatus.pending,
        )
        db.add(entry)

    db.commit()
    print("✅ Seed data inserted successfully!")
    print("\nTest accounts:")
    print("  Admin:    admin@fairprice.in / admin123")
    print("  Farmer:   farmer@fairprice.in / farmer123")
    print("  Consumer: consumer@fairprice.in / consumer123")
    print("  Vendor 1: vendor1@fairprice.in / vendor123")
    print("  Vendor 2: vendor2@fairprice.in / vendor123")


if __name__ == "__main__":
    seed()
    db.close()
