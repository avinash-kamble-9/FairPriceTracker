from fastapi import APIRouter
from app.api.v1.endpoints import auth, markets, prices, analytics, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(markets.router)
api_router.include_router(prices.router)
api_router.include_router(analytics.router)
api_router.include_router(users.router)
