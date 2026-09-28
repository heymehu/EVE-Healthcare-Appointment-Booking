import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(form);
      navigate(location.state?.from || "/centres");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={onSubmit}>
        <div className="brand" style={{ justifyContent: "center" }}>
          <span className="brand-mark">💙</span> EVE Healthcare
        </div>
        <h1>Welcome Back</h1>
        <p className="sub">Login to your account</p>
        {error && <div className="alert">{error}</div>}
        <div className="field">
          <label>Email</label>
          <div className="input-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" /><path d="M4 20c1.5-4 14.5-4 16 0" stroke="currentColor" /></svg>
            <input className="input" type="email" name="email" value={form.email} onChange={onChange} required placeholder="mehul@example.com" />
          </div>
        </div>
        <div className="field">
          <label>Password</label>
          <div className="input-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" /></svg>
            <input className="input" type="password" name="password" value={form.password} onChange={onChange} required placeholder="••••••••" />
          </div>
        </div>
        <button className="btn btn-primary btn-block" disabled={loading}>{loading ? "Logging in..." : "Login"}</button>
        <p className="switch">Don't have an account? <Link to="/signup">Sign Up</Link></p>
      </form>
    </div>
  );
}
