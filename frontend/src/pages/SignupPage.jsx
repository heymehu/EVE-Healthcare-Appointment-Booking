import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup(form);
      navigate("/centres");
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
        <h1>Create Your Account</h1>
        <p className="sub">Sign up to book diagnostic tests</p>
        {error && <div className="alert">{error}</div>}
        <div className="field">
          <label>Full Name</label>
          <div className="input-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" /><path d="M4 20c1.5-4 14.5-4 16 0" stroke="currentColor" /></svg>
            <input className="input" name="name" value={form.name} onChange={onChange} required placeholder="Your full name" />
          </div>
        </div>
        <div className="field">
          <label>Email</label>
          <div className="input-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" /><path d="M3 7l9 7 9-7" stroke="currentColor" /></svg>
            <input className="input" type="email" name="email" value={form.email} onChange={onChange} required placeholder="you@example.com" />
          </div>
        </div>
        <div className="field">
          <label>Password</label>
          <div className="input-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" /><path d="M8 11V8a4 4 0 018 0v3" stroke="currentColor" /></svg>
            <input className="input" type="password" name="password" value={form.password} onChange={onChange} required minLength={6} placeholder="••••••••" />
          </div>
        </div>
        <button className="btn btn-primary btn-block" disabled={loading}>{loading ? "Creating account..." : "Sign Up"}</button>
        <p className="switch">Already have an account? <Link to="/login">Login</Link></p>
      </form>
    </div>
  );
}
