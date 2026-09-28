import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { BookingAPI, CentreAPI, TestAPI } from "../api";
import { rupee } from "../constants";

function tomorrow() {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().slice(0, 10);
}

export default function BookTestPage() {
  const { centreId, testId } = useParams();
  const navigate = useNavigate();
  const [centre, setCentre] = useState(null);
  const [test, setTest] = useState(null);
  const [date, setDate] = useState(tomorrow());
  const [time, setTime] = useState("10:00");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([CentreAPI.get(centreId), TestAPI.get(testId)])
      .then(([centreData, testData]) => {
        setCentre(centreData);
        setTest(testData);
      })
      .catch((err) => setError(err.message));
  }, [centreId, testId]);

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const booking = await BookingAPI.create({
        centre_id: Number(centreId),
        test_id: Number(testId),
        appointment_date: date,
        appointment_time: `${time}:00`,
      });
      navigate(`/payment/${booking.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (!centre || !test) return <div className="container page"><p className="muted">Loading booking details...</p></div>;

  return (
    <div className="container page">
      <Link className="back" to={`/centres/${centreId}`}>← Back to Centre</Link>
      <div className="form-card card">
        <h1>Book Diagnostic Test</h1>
        {error && <div className="alert">{error}</div>}
        <div className="summary-section">
          <div className="kv"><span>Test</span><strong>{test.name}</strong></div>
          <div className="kv"><span>Centre</span><strong>{centre.name}, {centre.location.split(",")[0]}</strong></div>
          <div className="kv"><span>Price</span><strong>{rupee(test.price)}</strong></div>
        </div>
        <form onSubmit={onSubmit}>
          <div className="grid-2">
            <div className="field">
              <label>Appointment Date</label>
              <input className="input date-input" type="date" value={date} min={tomorrow()} onChange={(e) => setDate(e.target.value)} required />
            </div>
            <div className="field">
              <label>Appointment Time</label>
              <input className="input time-input" type="time" value={time} onChange={(e) => setTime(e.target.value)} required />
            </div>
          </div>
          <div className="total-row"><span>Total Amount</span><strong>{rupee(test.price)}</strong></div>
          <button className="btn btn-primary btn-block btn-lg" disabled={loading}>{loading ? "Creating booking..." : "Proceed to Payment →"}</button>
        </form>
      </div>
    </div>
  );
}

