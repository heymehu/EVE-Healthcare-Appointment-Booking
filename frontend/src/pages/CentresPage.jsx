import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CentreAPI } from "../api";
import {
  CENTRE_TYPES,
  CITIES,
  PANELS,
  RATING_FILTERS,
  SERVICE_CATEGORIES,
  SORT_OPTIONS,
  rupee,
  splitPanels,
} from "../constants";

const DEFAULT_FILTERS = {
  q: "",
  location: "",
  category: "all",
  centre_type: "all",
  panel: "",
  min_rating: "",
  max_price: "",
  sort: "relevance",
};

export default function CentresPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState(() => ({
    ...DEFAULT_FILTERS,
    ...Object.fromEntries(searchParams.entries()),
  }));
  const [data, setData] = useState({ items: [], total: 0 });
  const [cities, setCities] = useState(CITIES);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [panelOpen, setPanelOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    CentreAPI.cities()
      .then((res) => {
        if (!cancelled && Array.isArray(res) && res.length) setCities(res);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const result = await CentreAPI.list({
          q: filters.q,
          location: filters.location,
          category: filters.category === "all" ? "" : filters.category,
          centre_type: filters.centre_type === "all" ? "" : filters.centre_type,
          panel: filters.panel,
          min_rating: filters.min_rating,
          max_price: filters.max_price,
          sort: filters.sort,
        });
        setData(result);
        setError("");
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => clearTimeout(timer);
  }, [filters]);

  function update(patch) {
    const next = { ...filters, ...patch };
    setFilters(next);
    const params = new URLSearchParams();
    Object.entries(next).forEach(([key, value]) => {
      if (!value || value === "all" || (key === "sort" && value === "relevance")) return;
      params.set(key, value);
    });
    setSearchParams(params);
  }

  function resetAll() {
    setFilters(DEFAULT_FILTERS);
    setSearchParams({});
  }

  const activeCount = Object.entries(filters).filter(
    ([key, value]) =>
      value && value !== "all" && (key !== "sort" || value !== "relevance") && key !== "q"
  ).length;

  return (
    <div className="container page">
      <div className="page-header">
        <h1>Empaneled Hospitals, Diagnostic Centres &amp; Clinics</h1>
        <p className="muted">
          Filter by diagnostic section, centre type, empanelment panel, rating and price
        </p>
      </div>

      {/* Specialty Category Navigation Bar */}
      <div className="specialty-filter-bar">
        <button
          className={`specialty-pill ${filters.category === "all" ? "active" : ""}`}
          onClick={() => update({ category: "all" })}
        >
          <span className="pill-icon">🏥</span>
          <span className="pill-label">All Services</span>
        </button>
        {SERVICE_CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            className={`specialty-pill ${filters.category === cat.id ? "active" : ""}`}
            onClick={() => update({ category: cat.id })}
          >
            <span className="pill-icon">{cat.icon}</span>
            <span className="pill-label">{cat.name}</span>
          </button>
        ))}
      </div>

      <div className="listing-layout">
        {/* Filter Panel — mirrors the reference marketplace filter sidebar */}
        <aside className={`filter-panel ${panelOpen ? "open" : ""}`}>
          <div className="filter-head">
            <h3>Filters</h3>
            <button className="filter-close" onClick={() => setPanelOpen(false)} aria-label="Close filters">
              ×
            </button>
          </div>

          <div className="filter-block">
            <h4>Center Type</h4>
            {CENTRE_TYPES.map((type) => (
              <label key={type.id} className="check-row">
                <input
                  type="radio"
                  name="centre_type"
                  checked={filters.centre_type === type.id}
                  onChange={() => update({ centre_type: type.id })}
                />
                <span className="check-label">{type.icon} {type.label}</span>
              </label>
            ))}
          </div>

          <div className="filter-block">
            <h4>Panels</h4>
            {PANELS.map((panel) => (
              <label key={panel} className="check-row">
                <input
                  type="checkbox"
                  checked={filters.panel === panel}
                  onChange={() =>
                    update({ panel: filters.panel === panel ? "" : panel })
                  }
                />
                <span className="check-label">{panel}</span>
              </label>
            ))}
          </div>

          <div className="filter-block">
            <h4>Ratings</h4>
            {RATING_FILTERS.map((rating) => (
              <label key={rating.id} className="check-row">
                <input
                  type="radio"
                  name="rating"
                  checked={filters.min_rating === rating.id}
                  onChange={() => update({ min_rating: rating.id })}
                />
                <span className="check-label">
                  {rating.id === "all" ? rating.label : <><span className="star">★</span> {rating.label}</>}
                </span>
              </label>
            ))}
          </div>

          <div className="filter-block">
            <h4>Price Range</h4>
            <div className="price-filter">
              <input
                className="price-input"
                type="number"
                min="0"
                step="500"
                placeholder="Max ₹"
                value={filters.max_price}
                onChange={(e) => update({ max_price: e.target.value })}
              />
              <span className="muted">up to</span>
            </div>
          </div>

          <div className="filter-actions">
            <button className="btn btn-outline btn-sm" onClick={resetAll}>Clear All</button>
            <button className="btn btn-primary btn-sm" onClick={() => setPanelOpen(false)}>
              Apply Filters
            </button>
          </div>
        </aside>

        <div className="listing-main">
          {/* Search & Sort Toolbar */}
          <div className="toolbar">
            <div className="search-wrap">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="7" stroke="#94a3b8" strokeWidth="2" /><path d="M20 20l-3-3" stroke="#94a3b8" strokeWidth="2" strokeLineCap="round" /></svg>
              <input
                className="search"
                value={filters.q}
                onChange={(e) => update({ q: e.target.value })}
                placeholder="Search hospital, centre or test (e.g. Apollo, ECG, MRI)..."
              />
            </div>
            <select
              className="select"
              value={filters.location}
              onChange={(e) => update({ location: e.target.value })}
            >
              <option value="">All Locations</option>
              {cities.map((city) => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
            <select
              className="select sort-select"
              value={filters.sort}
              onChange={(e) => update({ sort: e.target.value })}
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div className="results-bar">
            <button className="btn btn-outline btn-sm filter-toggle" onClick={() => setPanelOpen(true)}>
              ☰ Filters{activeCount > 0 ? ` (${activeCount})` : ""}
            </button>
            <span className="muted">
              {loading ? "Searching…" : `${data.total} centre${data.total === 1 ? "" : "s"} found`}
            </span>
            {activeCount > 0 && (
              <button className="linkish" onClick={resetAll}>Clear all filters</button>
            )}
          </div>

          {error && <div className="alert">{error}</div>}
          {!loading && data.items.length === 0 && (
            <div className="empty-state card">
              <p className="muted">No diagnostic centres or hospitals found matching your selected criteria.</p>
              <button className="btn btn-outline btn-sm" onClick={resetAll}>
                Clear All Filters
              </button>
            </div>
          )}

          <div className="centre-list">
            {data.items.map((centre) => (
              <Link to={`/centres/${centre.id}`} className="centre-card" key={centre.id}>
                <div className="centre-card-img-wrap">
                  <img src={centre.image_url} alt={centre.name} loading="lazy" />
                </div>
                <div className="centre-card-info">
                  <h3>{centre.name}</h3>
                  <div className="meta">
                    📍 {centre.address ? `${centre.address}, ${centre.location}` : centre.location}
                  </div>
                  <p className="meta-desc">{centre.description}</p>
                  <div className="meta tags-row">
                    <span className="type-chip">{centre.centre_type}</span>
                    <span className="rating-badge"><span className="star">★</span> {centre.rating} ({centre.review_count} reviews)</span>
                    <span className="tests-count">🧪 {centre.available_tests} tests</span>
                    {centre.starting_price != null && (
                      <span className="from-price">from {rupee(centre.starting_price)}</span>
                    )}
                  </div>
                  <div className="hospital-tags">
                    {centre.accreditation && (
                      <span className="mini-tag verified">{centre.accreditation}</span>
                    )}
                    {splitPanels(centre.panels).map((panel) => (
                      <span key={panel} className="mini-tag">{panel}</span>
                    ))}
                  </div>
                </div>
                <span className="arrow" aria-hidden="true">›</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {panelOpen && <div className="filter-overlay" onClick={() => setPanelOpen(false)} />}
    </div>
  );
}
