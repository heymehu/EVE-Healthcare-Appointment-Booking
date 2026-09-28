import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CentreAPI } from "../api";
import { CATEGORY_BY_ID, CITIES, SERVICE_CATEGORIES, STATS, rupee, splitPanels } from "../constants";

const CITY_LABELS = ["Anywhere", ...CITIES];

function CategoryCard({ category, stats }) {
  const navigate = useNavigate();
  const stat = stats[category.id];
  return (
    <Link
      to={`/services/${encodeURIComponent(category.id)}`}
      className="category-card"
    >
      <div className="category-icon-box">{category.icon}</div>
      <div className="category-info">
        <h3>{category.name}</h3>
        <span className="category-badge">{category.badge}</span>
        <p>{category.desc}</p>
        <div className="category-meta">
          <span>{stat ? `${stat.centre_count} centres` : "—"}</span>
          <span className="dot">•</span>
          <span>{stat?.min_price ? `from ${rupee(stat.min_price)}` : "—"}</span>
        </div>
      </div>
      <span className="category-arrow" aria-hidden="true">›</span>
    </Link>
  );
}

function CentreCard({ centre, compact = false }) {
  const panels = splitPanels(centre.panels);
  return (
    <Link to={`/centres/${centre.id}`} className="hospital-card">
      <div className="hospital-img-wrap">
        <img src={centre.image_url} alt={centre.name} loading="lazy" />
        <span className="rating-tag">
          <span className="star">★</span> {centre.rating} ({centre.review_count})
        </span>
        <span className="type-tag">{centre.centre_type}</span>
      </div>
      <div className="hospital-body">
        <h3>{centre.name}</h3>
        <p className="hospital-location">📍 {centre.location}</p>
        {!compact && <p className="hospital-desc">{centre.description}</p>}
        <div className="hospital-tags">
          {centre.accreditation && <span className="mini-tag verified">{centre.accreditation}</span>}
          {panels.slice(0, 2).map((panel) => (
            <span key={panel} className="mini-tag">{panel}</span>
          ))}
        </div>
        <div className="hospital-footer">
          <span className="available-count">🧪 {centre.available_tests} tests</span>
          {centre.starting_price != null && (
            <span className="from-price">from {rupee(centre.starting_price)}</span>
          )}
        </div>
      </div>
    </Link>
  );
}

function ServiceSection({ category, centres, stats }) {
  const stat = stats[category.id];
  return (
    <section className="container section-block service-section">
      <div className="section-title-wrap flex-between">
        <div>
          <h2>
            <span className="section-emoji">{category.icon}</span> {category.name} Near You
          </h2>
          <p className="section-subtitle">
            {stat
              ? `${stat.test_count} ${category.short.toLowerCase()} tests across ${stat.centre_count} centres · from ${rupee(stat.min_price)}`
              : category.desc}
          </p>
        </div>
        <Link to={`/services/${encodeURIComponent(category.id)}`} className="view-all-link">
          View all {category.name} →
        </Link>
      </div>

      <div className="service-body service-body-full">
        <div className="service-cards">
          {centres.map((centre) => (
            <CentreCard key={centre.id} centre={centre} compact />
          ))}
        </div>
      </div>
    </section>
  );
}

export default function HomePage() {
  const navigate = useNavigate();
  const [featuredCentres, setFeaturedCentres] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [clinics, setClinics] = useState([]);
  const [diagnosticCentres, setDiagnosticCentres] = useState([]);
  const [serviceCentres, setServiceCentres] = useState({});
  const [stats, setStats] = useState({});
  const [query, setQuery] = useState("");
  const [city, setCity] = useState("");
  const [lookingFor, setLookingFor] = useState("");
  const [when, setWhen] = useState("");

  useEffect(() => {
    CentreAPI.categories()
      .then((res) => {
        const map = {};
        (res.items || []).forEach((item) => {
          map[item.id] = item;
        });
        setStats(map);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const cityParam = city && city !== "Anywhere" ? { location: city } : {};

    CentreAPI.list({ ...cityParam, page_size: 8 })
      .then((res) => setFeaturedCentres(res.items || []))
      .catch(() => {});

    CentreAPI.list({ ...cityParam, centre_type: "Hospital", page_size: 6 })
      .then((res) => setHospitals(res.items || []))
      .catch(() => {});

    CentreAPI.list({ ...cityParam, centre_type: "Clinic", page_size: 3 })
      .then((res) => setClinics(res.items || []))
      .catch(() => {});

    CentreAPI.list({ ...cityParam, centre_type: "Diagnostic Center", page_size: 6 })
      .then((res) => setDiagnosticCentres(res.items || []))
      .catch(() => {});
  }, [city]);

  useEffect(() => {
    let cancelled = false;
    const location = city && city !== "Anywhere" ? { location: city } : {};
    Promise.all(
      SERVICE_CATEGORIES.map((cat) =>
        CentreAPI.list({ ...location, category: cat.id, page_size: 4 })
          .then((res) => [cat.id, res.items || []])
          .catch(() => [cat.id, []])
      )
    ).then((pairs) => {
      if (cancelled) return;
      setServiceCentres(Object.fromEntries(pairs));
    });
    return () => {
      cancelled = true;
    };
  }, [city]);

  const minPrice = useMemo(() => {
    const category = CATEGORY_BY_ID[lookingFor];
    if (!category) return null;
    const stat = stats[lookingFor];
    return stat?.min_price ?? null;
  }, [lookingFor, stats]);

  function handleSearch(e) {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (lookingFor) params.set("category", lookingFor);
    if (city && city !== "Anywhere") params.set("location", city);
    const search = params.toString();
    navigate(search ? `/centres?${search}` : "/centres");
  }

  return (
    <div className="home-container">
      {/* Main Hero Section */}
      <section className="container hero-section">
        <div className="hero-content">
          <span className="hero-pill">✨ EVE Healthcare Diagnostic Marketplace</span>
          <h1>Book MRI, PET CT, Cardiology &amp; Blood Tests Online</h1>
          <p>
            Search empaneled hospitals, diagnostic centers and clinics across Delhi NCR.
            Compare transparent prices, pick a time slot and get same-day digital reports.
          </p>

          <form className="hero-search-bar hero-search-stack" onSubmit={handleSearch}>
            <div className="search-field">
              <span className="search-icon">📍</span>
              <input
                type="text"
                placeholder="Search hospital, centre or test (Apollo, ECG, MRI Brain)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>

            <div className="search-field">
              <span className="search-icon">🩺</span>
              <select value={lookingFor} onChange={(e) => setLookingFor(e.target.value)}>
                <option value="">Looking for: Any Diagnostic</option>
                {SERVICE_CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div className="search-field">
              <span className="search-icon">🏙️</span>
              <select value={city} onChange={(e) => setCity(e.target.value)}>
                {CITY_LABELS.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>

            <div className="search-field">
              <span className="search-icon">📅</span>
              <input
                type="date"
                value={when}
                onChange={(e) => setWhen(e.target.value)}
              />
            </div>

            <button type="submit" className="btn btn-primary btn-search">
              Search →
            </button>
          </form>

          {minPrice != null && (
            <p className="hero-hint">
              {CATEGORY_BY_ID[lookingFor]?.name} packages start at {rupee(minPrice)}
            </p>
          )}

          <div className="hero-quick-links">
            <span>Popular:</span>
            {["Cardiology", "Blood Test", "MRI Scan", "Full Body Checkup"].map((id) => (
              <Link key={id} to={`/services/${encodeURIComponent(id)}`}>
                {CATEGORY_BY_ID[id].name}
              </Link>
            ))}
          </div>
        </div>
        <div className="hero-image-wrapper" role="img" aria-label="EVE Healthcare Diagnostics" />
      </section>

      {/* Trust Stats Strip */}
      <section className="container stats-strip">
        {STATS.map((stat) => (
          <div className="stat-item" key={stat.label}>
            <strong>{stat.value}</strong>
            <span>{stat.label}</span>
          </div>
        ))}
      </section>

      {/* Specialties & Categories Section */}
      <section className="container section-block">
        <div className="section-title-wrap">
          <h2>Browse by Medical Specialty &amp; Test Section</h2>
          <p className="section-subtitle">
            Pick a department to see the tests it covers and the empaneled hospitals offering it
          </p>
        </div>
        <div className="category-grid">
          {SERVICE_CATEGORIES.map((cat) => (
            <CategoryCard key={cat.id} category={cat} stats={stats} />
          ))}
        </div>
      </section>

      {/* Cardiology Section */}
      <ServiceSection
        category={CATEGORY_BY_ID.Cardiology}
        centres={serviceCentres.Cardiology || []}
        stats={stats}
      />

      {/* Blood Test Section */}
      <ServiceSection
        category={CATEGORY_BY_ID["Blood Test"]}
        centres={serviceCentres["Blood Test"] || []}
        stats={stats}
      />

      {/* Imaging Sections */}
      <ServiceSection
        category={CATEGORY_BY_ID["MRI Scan"]}
        centres={serviceCentres["MRI Scan"] || []}
        stats={stats}
      />
      <ServiceSection
        category={CATEGORY_BY_ID["CT Scan"]}
        centres={serviceCentres["CT Scan"] || []}
        stats={stats}
      />

      {/* Hospitals Section */}
      <section className="container section-block">
        <div className="section-title-wrap flex-between">
          <div>
            <h2>🏥 Empaneled Hospitals</h2>
            <p className="section-subtitle">
              NABH &amp; NABL accredited super-specialty hospitals with in-house diagnostics
            </p>
          </div>
          <Link to="/centres?centre_type=Hospital" className="view-all-link">View All Hospitals →</Link>
        </div>
        <div className="hospitals-grid">
          {hospitals.map((centre) => (
            <CentreCard key={centre.id} centre={centre} />
          ))}
        </div>
      </section>

      {/* Diagnostic Centres & Clinics Section */}
      <section className="container section-block">
        <div className="section-title-wrap flex-between">
          <div>
            <h2>🔬 Diagnostic Centers &amp; Clinics</h2>
            <p className="section-subtitle">
              Standalone imaging centres, pathology labs and neighbourhood clinics
            </p>
          </div>
          <Link to="/centres" className="view-all-link">Browse All Centres →</Link>
        </div>
        <div className="split-type-grid">
          <div>
            <h3 className="type-heading">Diagnostic Centers</h3>
            <div className="hospitals-grid">
              {diagnosticCentres.map((centre) => (
                <CentreCard key={centre.id} centre={centre} />
              ))}
            </div>
          </div>
          <div>
            <h3 className="type-heading">Clinics</h3>
            <div className="hospitals-grid">
              {clinics.map((centre) => (
                <CentreCard key={centre.id} centre={centre} />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Top Rated Centres */}
      <section className="container section-block">
        <div className="section-title-wrap flex-between">
          <div>
            <h2>⭐ Top Rated Centres Near You</h2>
            <p className="section-subtitle">
              {city === "Anywhere" || !city
                ? "Highest rated diagnostics across all served cities"
                : `Highest rated diagnostics in ${city}`}
            </p>
          </div>
          <Link to="/centres?sort=rating" className="view-all-link">View All →</Link>
        </div>
        <div className="hospitals-grid">
          {featuredCentres.map((centre) => (
            <CentreCard key={centre.id} centre={centre} />
          ))}
        </div>
      </section>

      {/* Why Choose EVE Healthcare */}
      <section className="container section-block">
        <div className="section-title-wrap text-center">
          <h2>Why Choose EVE Healthcare?</h2>
        </div>
        <div className="features-row">
          <article className="feature-item">
            <div className="feature-icon">🛡️</div>
            <h3>Verified NABL &amp; ISO Labs</h3>
            <p>100% certified diagnostic labs &amp; super-specialty hospitals</p>
          </article>
          <article className="feature-item">
            <div className="feature-icon">⚡</div>
            <h3>Instant Online Booking</h3>
            <p>Select your appointment date and time slot instantly</p>
          </article>
          <article className="feature-item">
            <div className="feature-icon">💰</div>
            <h3>Transparent Pricing</h3>
            <p>Save up to 50% compared to direct hospital walk-ins</p>
          </article>
          <article className="feature-item">
            <div className="feature-icon">📄</div>
            <h3>Same-Day Digital Reports</h3>
            <p>Fast digital report delivery sent straight to your dashboard</p>
          </article>
          <article className="feature-item">
            <div className="feature-icon">🏥</div>
            <h3>Panel Accepted</h3>
            <p>CGHS, ECHS and corporate empanelment supported</p>
          </article>
          <article className="feature-item">
            <div className="feature-icon">🩺</div>
            <h3>All Specialties</h3>
            <p>Cardiology, neurology, imaging and full body packages</p>
          </article>
        </div>
      </section>
    </div>
  );
}
