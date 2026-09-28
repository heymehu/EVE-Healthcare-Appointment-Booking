import { useState, useEffect } from "react";
import { Link, NavLink, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { SERVICE_CATEGORIES } from "../constants";

function Logo() {
  return (
    <Link to="/" className="brand">
      <span className="brand-mark">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M19.5 12.5c1.2-1.4 2-3.1 2-5 0-3.3-2.5-5.5-5.5-5.5-1.7 0-3.2.8-4 2-0.8-1.2-2.3-2-4-2C4.5 2 2 4.2 2 7.5c0 6.2 8.8 11.7 10 12.5.3-.2 1.2-.8 2.3-1.7" stroke="#2563eb" strokeWidth="1.8" fill="#2563eb" />
          <path d="M12 13h3l2-4 2 7 1.5-3H23" stroke="#2563eb" strokeWidth="1.6" fill="none" />
        </svg>
      </span>
      <span className="brand-title">EVE Healthcare</span>
    </Link>
  );
}

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const [servicesOpen, setServicesOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    setOpen(false);
    setServicesOpen(false);
  }, [location.pathname]);

  return (
    <header className="navbar">
      <div className="container nav-inner">
        <Logo />
        <button
          className="menu-btn"
          onClick={() => setOpen((value) => !value)}
          aria-label="Toggle menu"
          aria-expanded={open}
        >
          {open ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="4" y1="6" x2="20" y2="6" />
              <line x1="4" y1="12" x2="20" y2="12" />
              <line x1="4" y1="18" x2="20" y2="18" />
            </svg>
          )}
        </button>
        <div className={`nav-menu ${open ? "open" : ""}`}>
          <nav className="nav-links">
            <NavLink to="/" end onClick={() => setOpen(false)}>Home</NavLink>

            <div
              className="nav-dropdown"
            >
              <button className="nav-dropdown-trigger" onClick={() => setServicesOpen((v) => !v)}>
                Services <span className="caret">▾</span>
              </button>
              {servicesOpen && (
                <div className="nav-dropdown-menu">
                  {SERVICE_CATEGORIES.map((cat) => (
                    <Link
                      key={cat.id}
                      to={`/services/${encodeURIComponent(cat.id)}`}
                      onClick={() => {
                        setOpen(false);
                        setServicesOpen(false);
                      }}
                    >
                      <span className="pill-icon">{cat.icon}</span>
                      <span>
                        <strong>{cat.name}</strong>
                        <em>{cat.badge}</em>
                      </span>
                    </Link>
                  ))}
                  <Link
                    className="nav-dropdown-all"
                    to="/centres"
                    onClick={() => {
                      setOpen(false);
                      setServicesOpen(false);
                    }}
                  >
                    View all centres →
                  </Link>
                </div>
              )}
            </div>

            <NavLink to="/centres" onClick={() => setOpen(false)}>Centres</NavLink>
            <NavLink to="/centres?centre_type=Hospital" onClick={() => setOpen(false)}>Hospitals</NavLink>
            <NavLink to="/bookings" onClick={() => setOpen(false)}>My Bookings</NavLink>
          </nav>
          <div className="nav-actions">
            {isAuthenticated ? (
              <div className="user-nav-group">
                <div className="avatar-info">
                  <div className="avatar" title={user?.name}>
                    {user?.name?.[0]?.toUpperCase() || "U"}
                  </div>
                  <span className="user-name-text">{user?.name || "User"}</span>
                </div>
                <button
                  className="logout-btn"
                  onClick={() => {
                    logout();
                    setOpen(false);
                    navigate("/");
                  }}
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="auth-nav-group">
                <Link className="btn btn-ghost" to="/login" onClick={() => setOpen(false)}>Login</Link>
                <Link className="btn btn-primary" to="/signup" onClick={() => setOpen(false)}>Sign Up</Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
