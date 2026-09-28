import random
import uuid

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import bad_request, forbidden, not_found
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentCreate

PAYMENT_TO_BOOKING_STATUS = {
    "SUCCESS": "CONFIRMED",
    "FAILED": "FAILED",
}


class PaymentService:
    def _load_booking(self, db: Session, booking_id: int) -> Booking:
        booking = (
            db.query(Booking)
            .options(joinedload(Booking.test), joinedload(Booking.centre))
            .filter(Booking.id == booking_id)
            .first()
        )
        if booking is None:
            raise not_found("Booking not found")
        return booking

    def simulate_outcome(self, requested: str) -> str:
        if requested in {"SUCCESS", "FAILED"}:
            return requested
        return "SUCCESS" if random.random() < 0.8 else "FAILED"

    def create_and_process(self, db: Session, user: User, payload: PaymentCreate) -> Payment:
        booking = self._load_booking(db, payload.booking_id)
        if booking.user_id != user.id:
            raise forbidden("You cannot pay for another user's booking")
        if booking.status == "CONFIRMED":
            raise bad_request("This booking is already confirmed")
        if booking.status == "CANCELLED":
            raise bad_request("Cannot pay for a cancelled booking")
        if booking.status not in {"PENDING", "FAILED"}:
            raise bad_request(f"Cannot pay for a booking with status {booking.status}")

        outcome = self.simulate_outcome(payload.simulate_status)
        event_id = f"evt_{uuid.uuid4().hex}"
        payment = Payment(
            booking_id=booking.id,
            status=outcome,
            provider_event_id=event_id,
        )
        booking.status = PAYMENT_TO_BOOKING_STATUS[outcome]
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return (
            db.query(Payment)
            .options(
                joinedload(Payment.booking).joinedload(Booking.test),
                joinedload(Payment.booking).joinedload(Booking.centre),
            )
            .filter(Payment.id == payment.id)
            .one()
        )


payment_service = PaymentService()
