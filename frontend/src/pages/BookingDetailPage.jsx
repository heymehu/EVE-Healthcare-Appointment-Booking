import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { BookingAPI } from "../api";
import StatusBadge from "../components/StatusBadge";
import { rupee } from "../constants";

export default function BookingDetailPage() {
  const { bookingId } = useParams();
  const [booking, setBooking] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    BookingAPI.get(bookingId).then(setBooking).catch((err) => setError(err.message));
  }, [bookingId]);

  if (error) return <div className="container page"><div className="alert">{error}</div></div>;
  if (!booking) return <div className="container page"><p className="muted">Loading booking details...</p></div>;

  return (
    <div className="container page">
      <Link className="back" to="/bookings">← Back to bookings</Link>
      <div className="form-card card">
        <h1>Booking #{booking.booking_code}</h1>
        <div className="summary-section">
          <div className="kv"><span>Test</span><strong>{booking.test?.name}</strong></div>
          <div className="kv"><span>Centre</span><strong>{booking.centre?.name}</strong></div>
          <div className="kv"><span>Date</span><strong>{booking.appointment_date}</strong></div>
          <div className="kv"><span>Time</span><strong>{String(booking.appointment_time).slice(0, 5)}</strong></div>
          <div className="kv"><span>Amount</span><strong>{rupee(booking.amount)}</strong></div>
          <div className="kv"><span>Status</span><StatusBadge status={booking.status} /></div>
        </div>
      </div>
    </div>
  );
}

