import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { CentreAPI } from "../api";
import { CATEGORY_BY_ID, rupee, splitPanels } from "../constants";

export default function CentreDetailPage() {
  const { centreId } = useParams();
  const navigate = useNavigate();
  const [centre, setCentre] = useState(null);
  const [tests, setTests] = useState([]);
  const [tab, setTab] = useState("tests");
  const [activeCategory, setActiveCategory] = useState("all");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([CentreAPI.get(centreId), CentreAPI.tests(centreId)])
      .then(([centreData, testData]) => {
        setCentre(centreData);
        setTests(testData);
      })
      .catch((err) => setError(err.message));
  }, [centreId]);

  const categories = useMemo(() => {
    const found = [...new Set(tests.map((test) => test.category))];
    return found.sort();
  }, [tests]);

  const visibleTests = useMemo(() => {
    if (activeCategory === "all") return tests;
    return tests.filter((test) => test.category === activeCategory);
  }, [tests, activeCategory]);

  if (error) return <div className="container page"><div className="alert">{error}</div></div>;
  if (!centre) return <div className="container page"><p className="muted">Loading centre...</p></div>;

  const panels = splitPanels(centre.panels);

  return (
    <div className="container page">
      <Link className="back" to="/centres">← Back to Centres</Link>

      <section className="centre-hero">
        <div className="centre-hero-img-wrap">
          <img src={centre.image_url} alt={centre.name} />
        </div>
        <div className="centre-hero-copy">
          <div className="tags-row">
            <span className="type-chip">{centre.centre_type}</span>
            {centre.accreditation && <span className="mini-tag verified">{centre.accreditation}</span>}
          </div>
          <h1>{centre.name}</h1>
          <p className="meta">📍 {centre.address ? `${centre.address}, ${centre.location}` : centre.location}</p>
          <p className="meta">
            <span className="star">★</span> {centre.rating} ({centre.review_count} reviews) · 🕘 {centre.open_time}
            {centre.phone ? ` · ☎ ${centre.phone}` : ""}
          </p>
          <div className="hospital-tags">
            {panels.map((panel) => (
              <span key={panel} className="mini-tag">{panel}</span>
            ))}
          </div>
        </div>
      </section>

      {categories.length > 1 && (
        <div className="category-chips">
          <button
            className={`chip ${activeCategory === "all" ? "active" : ""}`}
            onClick={() => setActiveCategory("all")}
          >
            All Services ({tests.length})
          </button>
          {categories.map((cat) => {
            const meta = CATEGORY_BY_ID[cat];
            return (
              <button
                key={cat}
                className={`chip ${activeCategory === cat ? "active" : ""}`}
                onClick={() => setActiveCategory(cat)}
              >
                {meta ? `${meta.icon} ${meta.name}` : cat}
              </button>
            );
          })}
        </div>
      )}

      <div className="tabs">
        <button className={tab === "tests" ? "active" : ""} onClick={() => setTab("tests")}>
          Available Tests ({visibleTests.length})
        </button>
        <button className={tab === "about" ? "active" : ""} onClick={() => setTab("about")}>
          About Centre
        </button>
        <button className={tab === "contact" ? "active" : ""} onClick={() => setTab("contact")}>
          Location &amp; Contact
        </button>
      </div>

      {tab === "about" && (
        <div className="card">
          <p style={{ margin: "0 0 16px", lineHeight: 1.6 }}>{centre.description}</p>
          <h3 className="sub-heading">Centre Information</h3>
          <div className="kv"><span>Center Type</span><strong>{centre.centre_type}</strong></div>
          <div className="kv"><span>Accreditation</span><strong>{centre.accreditation || "—"}</strong></div>
          <div className="kv"><span>Empanelment Panels</span><strong>{panels.join(", ") || "—"}</strong></div>
          <div className="kv"><span>Diagnostic Sections</span><strong>{categories.join(", ") || "—"}</strong></div>
          <div className="kv"><span>Tests Available</span><strong>{centre.available_tests}</strong></div>
          <div className="kv"><span>Starting Price</span><strong>{centre.starting_price != null ? rupee(centre.starting_price) : "—"}</strong></div>
        </div>
      )}

      {tab === "contact" && (
        <div className="card">
          <div className="kv"><span>Address</span><strong>{centre.address || "—"}</strong></div>
          <div className="kv"><span>City</span><strong>{centre.city || "—"}</strong></div>
          <div className="kv"><span>Pincode</span><strong>{centre.pincode || "—"}</strong></div>
          <div className="kv"><span>Phone</span><strong>{centre.phone || "—"}</strong></div>
          <div className="kv"><span>Working Hours</span><strong>{centre.open_time || "—"}</strong></div>
        </div>
      )}

      {tab === "tests" && (
        visibleTests.length === 0 ? (
          <div className="empty-state card">
            <p className="muted">No tests in this section at the moment.</p>
          </div>
        ) : (
          <div className="test-list">
            {visibleTests.map((test) => {
              const meta = CATEGORY_BY_ID[test.category];
              return (
                <div className="test-row" key={test.id}>
                  <div className="test-info">
                    <strong>{test.name}</strong>
                    <div className="meta">
                      {meta ? `${meta.icon} ${test.category}` : test.category}
                    </div>
                    {test.description && <p className="meta-desc">{test.description}</p>}
                  </div>
                  <div className="test-action">
                    <span className="price">{rupee(test.price)}</span>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => navigate(`/book/${centre.id}/${test.id}`)}
                    >
                      Book Test
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )
      )}
    </div>
  );
}
