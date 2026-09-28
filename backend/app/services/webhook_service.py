import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import bad_request, not_found
from app.models.booking import Booking
from app.models.payment import Payment
from app.schemas.payment import WebhookPayload, WebhookResponse
from app.services.payment_service import PAYMENT_TO_BOOKING_STATUS

logger = logging.getLogger(__name__)


class WebhookService:
    def process(self, db: Session, payload: WebhookPayload) -> WebhookResponse:
        if payload.status not in PAYMENT_TO_BOOKING_STATUS:
            raise bad_request("Invalid payment status")

        existing = db.query(Payment).filter(Payment.provider_event_id == payload.event_id).first()
        if existing is not None:
            logger.info("Duplicate webhook ignored event_id=%s", payload.event_id)
            return WebhookResponse(
                processed=False,
                idempotent=True,
                message="Duplicate event ignored",
                payment=self._load_payment(db, existing.id),
            )

        payment = db.get(Payment, payload.payment_id)
        booking = db.get(Booking, payload.booking_id)
        if payment is None:
            raise not_found("Payment not found")
        if booking is None:
            raise not_found("Booking not found")
        if payment.booking_id != booking.id:
            raise bad_request("Payment does not belong to the given booking")

        payment.status = payload.status
        if booking.status != "CANCELLED":
            booking.status = PAYMENT_TO_BOOKING_STATUS[payload.status]
        payment.provider_event_id = payload.event_id

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            duplicate = db.query(Payment).filter(Payment.provider_event_id == payload.event_id).first()
            if duplicate is None:
                raise
            return WebhookResponse(
                processed=False,
                idempotent=True,
                message="Duplicate event ignored",
                payment=self._load_payment(db, duplicate.id),
            )

        logger.info(
            "Webhook applied event_id=%s payment_id=%s booking_id=%s status=%s",
            payload.event_id,
            payment.id,
            booking.id,
            payload.status,
        )
        return WebhookResponse(
            processed=True,
            idempotent=False,
            message="Webhook processed",
            payment=self._load_payment(db, payment.id),
        )

    def _load_payment(self, db: Session, payment_id: int) -> Payment:
        return (
            db.query(Payment)
            .options(
                joinedload(Payment.booking).joinedload(Booking.test),
                joinedload(Payment.booking).joinedload(Booking.centre),
            )
            .filter(Payment.id == payment_id)
            .one()
        )


webhook_service = WebhookService()
