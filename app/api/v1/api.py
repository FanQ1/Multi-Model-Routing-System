
from fastapi import APIRouter
from app.api.v1.endpoints import page1, page2

api_router = APIRouter()

api_router.include_router(page1.router, prefix="/page1", tags=["page1"])
api_router.include_router(page2.router, prefix="/page2", tags=["page2"])
