from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingListResponse, BookingOut
from app.services.booking_service import booking_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def _load(db: Session, booking_id: int) -> Booking:
    return (
        db.query(Booking)
        .options(joinedload(Booking.test), joinedload(Booking.centre))
        .filter(Booking.id == booking_id)
        .one()
    )


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingOut:
    booking = booking_service.create(db, current_user, payload)
    return BookingOut.model_validate(_load(db, booking.id))


@router.get("/", response_model=BookingListResponse)
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingListResponse:
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.test), joinedload(Booking.centre))
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return BookingListResponse(
        items=[BookingOut.model_validate(item) for item in bookings],
        total=len(bookings),
    )


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingOut:
    booking = booking_service.get_owned(db, current_user, booking_id)
    return BookingOut.model_validate(_load(db, booking.id))


@router.patch("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingOut:
    booking = booking_service.cancel(db, current_user, booking_id)
    return BookingOut.model_validate(_load(db, booking.id))
