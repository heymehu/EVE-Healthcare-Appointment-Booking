import logging
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

celery_app = Celery(
    "eve_healthcare",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.webhook_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
)

celery_app.autodiscover_tasks(["app.tasks"])


@worker_process_init.connect
def init_worker(**kwargs):
    logger.info("Celery worker initialized")


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    logger.info("Celery worker shutting down")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_webhook_retry(self, event_id: str, payment_id: int, booking_id: int, status: str):
    from app.core.database import SessionLocal
    from app.models.booking import Booking
    from app.models.payment import Payment
    from app.services.payment_service import PAYMENT_TO_BOOKING_STATUS
    from app.services.webhook_service import webhook_service
    from app.schemas.payment import WebhookPayload

    db = SessionLocal()
    try:
        existing = db.query(Payment).filter(Payment.provider_event_id == event_id).first()
        if existing is not None:
            logger.info("Duplicate webhook ignored event_id=%s", event_id)
            return {"processed": False, "idempotent": True, "message": "Duplicate event ignored"}

        payment = db.get(Payment, payment_id)
        booking = db.get(Booking, booking_id)
        if payment is None:
            logger.error("Payment not found: %s", payment_id)
            return {"processed": False, "error": "Payment not found"}
        if booking is None:
            logger.error("Booking not found: %s", booking_id)
            return {"processed": False, "error": "Booking not found"}
        if payment.booking_id != booking.id:
            logger.error("Payment does not belong to booking")
            return {"processed": False, "error": "Payment does not belong to the given booking"}

        payment.status = status
        if booking.status != "CANCELLED":
            booking.status = PAYMENT_TO_BOOKING_STATUS[status]
        payment.provider_event_id = event_id

        db.commit()
        logger.info("Webhook applied event_id=%s payment_id=%s booking_id=%s status=%s", event_id, payment_id, booking_id, status)
        return {"processed": True, "idempotent": False, "message": "Webhook processed"}
    except Exception as exc:
        logger.error("Webhook processing failed: %s", exc)
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task
def send_booking_notification(booking_id: int, notification_type: str):
    logger.info("Sending notification for booking %s: %s", booking_id, notification_type)
    return {"sent": True, "booking_id": booking_id, "type": notification_type}


@celery_app.task
def cleanup_expired_bookings():
    from app.core.database import SessionLocal
    from app.models.booking import Booking
    from datetime import date

    db = SessionLocal()
    try:
        expired = db.query(Booking).filter(
            Booking.status == "PENDING",
            Booking.appointment_date < date.today()
        ).all()
        for booking in expired:
            booking.status = "FAILED"
        db.commit()
        logger.info("Cleaned up %d expired bookings", len(expired))
        return {"cleaned": len(expired)}
    finally:
        db.close()