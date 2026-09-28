import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BookingAPI } from "../api";
import StatusBadge from "../components/StatusBadge";
import { rupee } from "../constants";

export default function BookingsPage() {
  const [data, setData] = useState({ items: [] });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function load() {
    setLoading(true);
    try {
      setData(await BookingAPI.list());
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function cancel(id) {
    if (!window.confirm("Are you sure you want to cancel this booking?")) return;
    try {
      await BookingAPI.cancel(id);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container page">
      <div className="page-header">
        <h1>My Bookings</h1>
        <p className="muted">View and manage your diagnostic test bookings</p>
      </div>

      {error && <div className="alert">{error}</div>}
      {loading && <p className="muted">Loading bookings...</p>}

      {!loading && data.items.length === 0 && (
        <div className="empty-state card">
          <p className="muted" style={{ margin: "0 0 16px" }}>No bookings found yet.</p>
          <button className="btn btn-primary" onClick={() => navigate("/centres")}>
            Explore Diagnostic Centres →
          </button>
        </div>
      )}

      {!loading && data.items.length > 0 && (
        <>
          {/* Desktop & Tablet Table View */}
          <div className="table-wrap desktop-only">
            <table>
              <thead>
                <tr>
                  <th>Booking ID</th>
                  <th>Test</th>
                  <th>Centre</th>
                  <th>Date & Time</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((booking) => (
                  <tr key={booking.id}>
                    <td><strong>#{booking.booking_code}</strong></td>
                    <td>{booking.test?.name}</td>
                    <td>{booking.centre?.name}</td>
                    <td>{booking.appointment_date}, {String(booking.appointment_time).slice(0, 5)}</td>
                    <td><strong>{rupee(booking.amount)}</strong></td>
                    <td><StatusBadge status={booking.status} /></td>
                    <td>
                      <div className="table-actions">
                        <button className="linkish" onClick={() => navigate(`/bookings/${booking.id}`)}>View</button>
                        {["PENDING", "CONFIRMED"].includes(booking.status) && (
                          <button className="linkish danger" onClick={() => cancel(booking.id)}>Cancel</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card View */}
          <div className="booking-cards-mobile mobile-only">
            {data.items.map((booking) => (
              <div className="booking-card-item card" key={booking.id}>
                <div className="booking-card-header">
                  <span className="booking-id-tag">#{booking.booking_code}</span>
                  <StatusBadge status={booking.status} />
                </div>
                <div className="booking-card-body">
                  <h3 className="booking-test-title">{booking.test?.name}</h3>
                  <p className="booking-centre-name">📍 {booking.centre?.name}</p>
                  <div className="booking-card-meta">
                    <span>📅 {booking.appointment_date}</span>
                    <span>⏰ {String(booking.appointment_time).slice(0, 5)}</span>
                  </div>
                  <div className="booking-card-price">
                    <span className="muted">Total Amount</span>
                    <strong className="price-tag">{rupee(booking.amount)}</strong>
                  </div>
                </div>
                <div className="booking-card-actions">
                  <button className="btn btn-outline btn-sm btn-block" onClick={() => navigate(`/bookings/${booking.id}`)}>View Details</button>
                  {["PENDING", "CONFIRMED"].includes(booking.status) && (
                    <button className="btn btn-danger-outline btn-sm btn-block" onClick={() => cancel(booking.id)}>Cancel</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

