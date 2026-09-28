import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { BookingAPI, PaymentAPI } from "../api";
import StatusBadge from "../components/StatusBadge";
import { rupee } from "../constants";

export default function PaymentPage() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [simulate, setSimulate] = useState("SUCCESS");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    BookingAPI.get(bookingId).then(setBooking).catch((err) => setError(err.message));
  }, [bookingId]);

  async function pay() {
    setLoading(true);
    setError("");
    try {
      const payment = await PaymentAPI.create({
        booking_id: Number(bookingId),
        simulate_status: simulate,
      });
      const path = payment.status === "SUCCESS" ? "success" : "failed";
      navigate(`/payment/${path}/${bookingId}`, { state: { payment } });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (!booking) return <div className="container page"><p className="muted">Loading payment details...</p></div>;

  const when = `${booking.appointment_date} ${String(booking.appointment_time).slice(0, 5)}`;

  return (
    <div className="container page">
      <Link className="back" to={`/book/${booking.centre_id}/${booking.test_id}`}>← Back</Link>
      <div className="form-card card">
        <h1>Payment (Simulated)</h1>
        <p className="note">This is a mock payment for testing purposes. No real card will be charged.</p>
        {error && <div className="alert">{error}</div>}
        <div className="summary-section">
          <div className="kv"><span>Test</span><strong>{booking.test?.name}</strong></div>
          <div className="kv"><span>Centre</span><strong>{booking.centre?.name}</strong></div>
          <div className="kv"><span>Date & Time</span><strong>{when}</strong></div>
          <div className="kv"><span>Amount</span><strong>{rupee(booking.amount)}</strong></div>
        </div>
        <h3 className="section-subtitle">Simulate Payment Result</h3>
        <div className="payment-options">
          <button type="button" className={`pay-option success ${simulate === "SUCCESS" ? "active" : ""}`} onClick={() => setSimulate("SUCCESS")}>
            <span>Success (80% chance)</span>
            {simulate === "SUCCESS" && <span className="checkmark">✓</span>}
          </button>
          <button type="button" className={`pay-option failed ${simulate === "FAILED" ? "active" : ""}`} onClick={() => setSimulate("FAILED")}>
            <span>Failed (20% chance)</span>
            {simulate === "FAILED" && <span className="checkmark">✓</span>}
          </button>
        </div>
        <p className="muted note-sm">Selecting an option forces that result. Use Auto for random 80/20 odds.</p>
        <div className="pay-actions-wrap">
          <button className="btn btn-outline" disabled={loading} onClick={() => { setSimulate("AUTO"); }}>Use 80/20 Auto</button>
          <button className="btn btn-primary btn-block btn-lg" disabled={loading} onClick={pay}>{loading ? "Processing..." : "Pay Now →"}</button>
        </div>
      </div>
    </div>
  );
}

export function PaymentResultPage({ kind }) {
  const { bookingId } = useParams();
  const [booking, setBooking] = useState(null);

  useEffect(() => {
    BookingAPI.get(bookingId).then(setBooking).catch(() => setBooking(null));
  }, [bookingId]);

  if (!booking) return <div className="container page"><p className="muted">Loading result...</p></div>;

  const ok = kind === "success";
  return (
    <div className="container page">
      <div className="result-card card">
        <div className={`result-icon ${ok ? "ok" : "bad"}`}>{ok ? "✓" : "✕"}</div>
        <h2>{ok ? "Payment Successful!" : "Payment Failed"}</h2>
        <p className="muted">
          {ok ? "Your diagnostic test has been booked successfully." : "Your payment could not be processed."}
        </p>
        <div className="result-details">
          <div className="kv"><span>Booking ID</span><strong>#{booking.booking_code}</strong></div>
          <div className="kv"><span>Test</span><strong>{booking.test?.name}</strong></div>
          <div className="kv"><span>Centre</span><strong>{booking.centre?.name}</strong></div>
          <div className="kv"><span>Date</span><strong>{booking.appointment_date}</strong></div>
          <div className="kv"><span>Time</span><strong>{String(booking.appointment_time).slice(0, 5)}</strong></div>
          <div className="kv"><span>Amount</span><strong>{rupee(booking.amount)}</strong></div>
          <div className="kv"><span>Status</span><StatusBadge status={booking.status} /></div>
        </div>
        <div className="result-actions">
          {ok ? (
            <Link className="btn btn-primary btn-block btn-lg" to="/bookings">View My Bookings →</Link>
          ) : (
            <Link className="btn btn-primary btn-block btn-lg" to={`/payment/${booking.id}`}>Try Again ↺</Link>
          )}
        </div>
      </div>
    </div>
  );
}

