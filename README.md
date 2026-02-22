# 🟢 FairPrice Tracker — Backend

FastAPI + PostgreSQL backend for crowd-sourced retail price tracking in Mumbai markets.

---

## 📁 Folder Structure

```
fairprice-backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/
│   │   └── v1/
│   │       ├── router.py          # Registers all routes
│   │       └── endpoints/
│   │           ├── auth.py        # Register / Login
│   │           ├── markets.py     # Cities, Markets, Products
│   │           ├── prices.py      # Vendor submissions + Admin review
│   │           ├── analytics.py   # Price stats, trends, spike alerts
│   │           └── users.py       # User management
│   ├── core/
│   │   ├── config.py              # Settings from .env
│   │   └── security.py            # JWT + bcrypt + role guards
│   ├── db/
│   │   └── database.py            # SQLAlchemy engine + session
│   ├── models/
│   │   ├── user.py                # User model + roles enum
│   │   ├── market.py              # City, Market, Product, Category
│   │   └── price_entry.py         # PriceEntry, VendorProfile
│   ├── schemas/
│   │   └── schemas.py             # All Pydantic models
│   └── services/
│       ├── auth_service.py        # Register/login logic
│       ├── price_service.py       # CRUD for price entries
│       └── analytics_service.py   # Moving avg, spike detection, trends
├── seed.py                        # Seed Mumbai data
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🚀 Quick Start (Docker — Recommended)

```bash
# 1. Clone and enter directory
cd fairprice-backend

# 2. Start Postgres + API
docker-compose up --build

# 3. Seed initial data (in a new terminal)
docker-compose exec api python seed.py
```

API will be live at: **http://localhost:8000**  
Docs (Swagger): **http://localhost:8000/docs**

---

## 🛠 Manual Setup (Without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL connection

# 4. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE fairprice_db;"

# 5. Run the server
uvicorn app.main:app --reload

# 6. Seed data
python seed.py
```

---

## 🔑 Test Accounts (after seeding)

| Role     | Email                      | Password    |
|----------|----------------------------|-------------|
| Admin    | admin@fairprice.in         | admin123    |
| Farmer   | farmer@fairprice.in        | farmer123   |
| Consumer | consumer@fairprice.in      | consumer123 |
| Vendor 1 | vendor1@fairprice.in       | vendor123   |
| Vendor 2 | vendor2@fairprice.in       | vendor123   |

---

## 📡 Key API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login → get JWT token |

### Markets & Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cities` | List all cities |
| GET | `/api/v1/markets?city_id=1` | List markets |
| GET | `/api/v1/products` | List all products |

### Vendor
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/prices` | Submit price entry |
| GET | `/api/v1/prices/my-submissions` | View own submissions |
| PATCH | `/api/v1/prices/{id}` | Edit pending submission |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/prices` | View all submissions (filter by status/product/market) |
| POST | `/api/v1/admin/prices/{id}/review` | Approve or reject |
| GET | `/api/v1/users/` | List all users |

### Analytics (public — no auth needed)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/product/{id}/market/{id}` | Full analytics: today avg, spike, 30-day trend |
| GET | `/api/v1/analytics/product/{id}/all-markets` | Compare product price across all Mumbai markets |
| GET | `/api/v1/analytics/fluctuating-products` | Top volatile products |

---

## 🌐 Deploying Backend (for Vercel frontend)

Recommended free/cheap options:
- **Railway.app** — Easiest. Connect GitHub, add Postgres, set env vars.
- **Render.com** — Free tier available. Uses Dockerfile.
- **Fly.io** — Fast, global edge deployment.

After deploying, set `CORS allow_origins` in `app/main.py` to your Vercel URL.

---

## 🧠 Business Logic Summary

- Only **approved** entries appear in analytics
- Spike alert = today's avg > 7-day moving avg by more than **20%**
- Vendors can only edit their own **pending** entries
- All aggregations (avg, min, max) are computed **dynamically** via SQL
- Architecture supports multi-city expansion via `city_id` on all relevant models
