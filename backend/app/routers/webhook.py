from fastapi import APIRouter

from app.routers.payments import router as payments_router

# Webhook lives on the payments router as POST /payments/webhook/
webhook_router = APIRouter()
