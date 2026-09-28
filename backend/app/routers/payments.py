from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import unauthorized, AppError
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut, WebhookPayload, WebhookResponse
from app.services.payment_service import payment_service
from app.services.webhook_service import webhook_service

router = APIRouter(prefix="/payments", tags=["Payments"])


def _queue_webhook_retry(payload: WebhookPayload) -> bool:
    """Queue webhook for retry via Celery if available."""
    try:
        from app.core.redis import REDIS_AVAILABLE
        if not REDIS_AVAILABLE:
            return False
        from app.tasks.webhook_tasks import process_webhook_retry
        process_webhook_retry.delay(
            event_id=payload.event_id,
            payment_id=payload.payment_id,
            booking_id=payload.booking_id,
            status=payload.status,
        )
        return True
    except Exception:
        return False


@router.post("/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentOut:
    payment = payment_service.create_and_process(db, current_user, payload)
    return PaymentOut.model_validate(payment)


@router.post("/webhook/", response_model=WebhookResponse)
async def payment_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None),
) -> WebhookResponse:
    settings = get_settings()
    if settings.WEBHOOK_SECRET and x_webhook_secret != settings.WEBHOOK_SECRET:
        raise unauthorized("Invalid webhook secret")

    # Try synchronous processing first
    try:
        return webhook_service.process(db, payload)
    except AppError as e:
        # Don't retry 4xx errors - they're client errors, not transient
        if e.status_code < 500:
            raise
        # For 5xx errors, queue for retry
        queued = _queue_webhook_retry(payload)
        return WebhookResponse(
            processed=False,
            idempotent=False,
            message="Webhook queued for retry" if queued else "Webhook processing failed; retry not available",
            payment=None,
        )
    except Exception:
        # If processing fails due to transient error, queue for retry via Celery if available
        queued = _queue_webhook_retry(payload)
        return WebhookResponse(
            processed=False,
            idempotent=False,
            message="Webhook queued for retry" if queued else "Webhook processing failed; retry not available",
            payment=None,
        )