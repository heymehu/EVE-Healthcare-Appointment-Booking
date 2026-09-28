from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.core.exceptions import bad_request, forbidden, not_found
from app.models.booking import Booking
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.test import DiagnosticTest
from app.models.user import User
from app.schemas.booking import BookingCreate

CANCELLABLE_STATUSES = {"PENDING", "CONFIRMED"}


class BookingService:
    def create(self, db: Session, user: User, payload: BookingCreate) -> Booking:
        centre = db.get(DiagnosticCentre, payload.centre_id)
        if centre is None:
            raise not_found("Diagnostic centre not found")

        test = db.get(DiagnosticTest, payload.test_id)
        if test is None:
            raise not_found("Diagnostic test not found")
        if test.centre_id != payload.centre_id:
            raise bad_request("Selected test does not belong to the given centre")

        appointment_dt = datetime.combine(payload.appointment_date, payload.appointment_time)
        if appointment_dt < datetime.now():
            raise bad_request("Appointment date and time cannot be in the past")

        if payload.appointment_time < time(7, 0) or payload.appointment_time > time(20, 0):
            raise bad_request("Appointment time must be between 07:00 and 20:00")

        booking = Booking(
            user_id=user.id,
            test_id=test.id,
            centre_id=centre.id,
            appointment_date=payload.appointment_date,
            appointment_time=payload.appointment_time,
            amount=test.price,
            status="PENDING",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    def list_for_user(self, db: Session, user: User) -> list[Booking]:
        return (
            db.query(Booking)
            .filter(Booking.user_id == user.id)
            .order_by(Booking.created_at.desc())
            .all()
        )

    def get_owned(self, db: Session, user: User, booking_id: int) -> Booking:
        booking = db.get(Booking, booking_id)
        if booking is None:
            raise not_found("Booking not found")
        if booking.user_id != user.id:
            raise forbidden("You cannot access another user's booking")
        return booking

    def cancel(self, db: Session, user: User, booking_id: int) -> Booking:
        booking = self.get_owned(db, user, booking_id)
        if booking.status not in CANCELLABLE_STATUSES:
            raise bad_request(f"Cannot cancel a booking with status {booking.status}")
        if booking.appointment_date < date.today():
            raise bad_request("Cannot cancel a past appointment")
        booking.status = "CANCELLED"
        db.commit()
        db.refresh(booking)
        return booking


booking_service = BookingService()
