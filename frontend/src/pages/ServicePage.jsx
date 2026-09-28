import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { CentreAPI } from "../api";
import {
  CATEGORY_BY_ID,
  SERVICE_CATEGORIES,
  rupee,
  splitPanels,
} from "../constants";

export default function ServicePage() {
  const { category } = useParams();
  const [searchParams] = useSearchParams();
  const locationFilter = searchParams.get("location") || "";
  const [centres, setCentres] = useState([]);
  const [stat, setStat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const meta = CATEGORY_BY_ID[category];
  const displayName = meta?.name || category || "Diagnostics";

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    CentreAPI.list({ category, location: locationFilter, page_size: 60, sort: "rating" })
      .then((res) => {
        if (cancelled) return;
        setCentres(res.items || []);
        setError("");
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [category, locationFilter]);

  useEffect(() => {
    let cancelled = false;
    CentreAPI.categories()
      .then((res) => {
        if (cancelled) return;
        setStat((res.items || []).find((item) => item.id === category) || null);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [category]);

  if (!meta) {
    return (
      <div className="container page">
        <div className="empty-state card">
          <p className="muted">Unknown diagnostic section.</p>
          <Link className="btn btn-outline btn-sm" to="/centres">Browse all centres</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container page">
      <nav className="breadcrumb">
        <Link to="/">Home</Link> <span>/</span> <strong>{displayName}</strong>
      </nav>

      <section className="service-hero">
        <div>
          <span className="hero-pill">{meta.icon} {meta.badge}</span>
          <h1>{displayName} Tests &amp; Diagnostics</h1>
          <p>{meta.desc}</p>
          <div className="service-hero-actions">
            <Link to={`/centres?category=${encodeURIComponent(category)}`} className="btn btn-primary">
              Book {displayName}
            </Link>
            <Link to="/centres" className="btn btn-outline">All Centres</Link>
          </div>
        </div>
        <div className="service-hero-stats">
          <div>
            <strong>{centres.length}</strong>
            <span>Centres</span>
          </div>
          <div>
            <strong>{stat?.test_count ?? "—"}</strong>
            <span>Tests listed</span>
          </div>
          <div>
            <strong>{stat?.min_price != null ? rupee(stat.min_price) : "—"}</strong>
            <span>Starting price</span>
          </div>
        </div>
      </section>

      <section className="section-block">
        <div className="section-title-wrap flex-between">
          <h2 className="sub-heading" style={{ margin: 0 }}>
            Centres offering {displayName}
            {locationFilter ? ` in ${locationFilter}` : ""}
          </h2>
          <Link to="/centres" className="view-all-link">See all →</Link>
        </div>

        {error && <div className="alert">{error}</div>}
        {loading && <p className="muted">Loading {displayName.toLowerCase()} centres...</p>}
        {!loading && centres.length === 0 && (
          <div className="empty-state card">
            <p className="muted">
              No centres currently offer {displayName.toLowerCase()}
              {locationFilter ? ` in ${locationFilter}` : ""}.
            </p>
            <Link to="/centres" className="btn btn-outline btn-sm">Clear filters</Link>
          </div>
        )}

        <div className="centre-list">
          {centres.map((centre) => (
            <Link to={`/centres/${centre.id}`} className="centre-card" key={centre.id}>
              <div className="centre-card-img-wrap">
                <img src={centre.image_url} alt={centre.name} loading="lazy" />
              </div>
              <div className="centre-card-info">
                <h3>{centre.name}</h3>
                <div className="meta">📍 {centre.location}</div>
                <div className="meta tags-row">
                  <span className="type-chip">{centre.centre_type}</span>
                  <span className="rating-badge"><span className="star">★</span> {centre.rating} ({centre.review_count})</span>
                  <span className="tests-count">🧪 {centre.available_tests} tests</span>
                  {centre.starting_price != null && (
                    <span className="from-price">from {rupee(centre.starting_price)}</span>
                  )}
                </div>
                <div className="hospital-tags">
                  {centre.accreditation && (
                    <span className="mini-tag verified">{centre.accreditation}</span>
                  )}
                  {splitPanels(centre.panels).slice(0, 3).map((panel) => (
                    <span key={panel} className="mini-tag">{panel}</span>
                  ))}
                </div>
              </div>
              <span className="arrow" aria-hidden="true">›</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section-block">
        <h2 className="sub-heading">Other Diagnostic Sections</h2>
        <div className="category-grid">
          {SERVICE_CATEGORIES.filter((cat) => cat.id !== category).map((cat) => (
            <Link
              key={cat.id}
              to={`/services/${encodeURIComponent(cat.id)}`}
              className="category-card"
            >
              <div className="category-icon-box">{cat.icon}</div>
              <div className="category-info">
                <h3>{cat.name}</h3>
                <span className="category-badge">{cat.badge}</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
