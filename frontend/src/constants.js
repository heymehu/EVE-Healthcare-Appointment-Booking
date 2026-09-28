export const SERVICE_CATEGORIES = [
  {
    id: "Cardiology",
    name: "Cardiology",
    icon: "❤️",
    short: "Heart care",
    badge: "ECG, ECHO, TMT, Holter",
    desc: "Heart health screening, cardiac markers and rhythm diagnostics.",
  },
  {
    id: "Blood Test",
    name: "Blood Tests",
    icon: "🩸",
    short: "Pathology",
    badge: "CBC, HbA1c, Thyroid, LFT",
    desc: "Routine and specialised pathology with home sample collection.",
  },
  {
    id: "MRI Scan",
    name: "MRI Scans",
    icon: "🧠",
    short: "MRI",
    badge: "Brain, Spine, Joints, Cardiac",
    desc: "High-definition magnetic resonance imaging on 1.5T to 3T machines.",
  },
  {
    id: "CT Scan",
    name: "CT & PET Scans",
    icon: "⚡",
    short: "CT / PET",
    badge: "PET-CT, Angiography, HRCT",
    desc: "Low-dose CT and molecular PET-CT imaging for precise diagnosis.",
  },
  {
    id: "Ultrasound",
    name: "Ultrasound & Doppler",
    icon: "🔊",
    short: "Ultrasound",
    badge: "USG, Colour Doppler",
    desc: "Sonography and vascular doppler studies with no radiation.",
  },
  {
    id: "X-Ray",
    name: "X-Ray & Radiology",
    icon: "🦴",
    short: "X-Ray",
    badge: "Digital X-Ray, DEXA",
    desc: "Low-dose digital radiography and bone density screening.",
  },
  {
    id: "Neurology",
    name: "Neurology",
    icon: "🧩",
    short: "Neuro",
    badge: "EEG, Nerve Conduction",
    desc: "Brain activity mapping and peripheral nerve signal studies.",
  },
  {
    id: "Full Body Checkup",
    name: "Health Packages",
    icon: "🏥",
    short: "Packages",
    badge: "Full Body Checkup",
    desc: "70+ parameter preventive screening packages for every age.",
  },
];

export const CATEGORY_IDS = SERVICE_CATEGORIES.map((cat) => cat.id);

export const CATEGORY_BY_ID = Object.fromEntries(
  SERVICE_CATEGORIES.map((cat) => [cat.id, cat])
);

export const CENTRE_TYPES = [
  { id: "all", label: "All Types", icon: "🏥" },
  { id: "Hospital", label: "Hospitals", icon: "🏥" },
  { id: "Clinic", label: "Clinics", icon: "🩺" },
  { id: "Diagnostic Center", label: "Diagnostic Centers", icon: "🔬" },
];

export const PANELS = ["CGHS", "ECHS", "Corporate Empanelment"];

export const RATING_FILTERS = [
  { id: "all", label: "All Ratings" },
  { id: "4.5", label: "4.5★ & above" },
  { id: "4", label: "4★ & above" },
  { id: "3", label: "3★ & above" },
  { id: "2", label: "2★ & above" },
];

export const SORT_OPTIONS = [
  { id: "relevance", label: "Relevance" },
  { id: "rating", label: "Highest Rating" },
  { id: "price_low", label: "Price: Low to High" },
  { id: "price_high", label: "Price: High to Low" },
  { id: "name", label: "Name: A to Z" },
];

export const CITIES = ["New Delhi", "Noida", "Gurugram", "Ghaziabad", "Faridabad", "Mumbai"];

export const STATS = [
  { value: "24+", label: "Empaneled Centres" },
  { value: "190+", label: "Tests & Scans Bookable" },
  { value: "5", label: "Cities Covered" },
  { value: "4.6★", label: "Average Patient Rating" },
];

export function rupee(value) {
  return `₹ ${Number(value ?? 0).toLocaleString("en-IN")}`;
}

export function splitPanels(panels) {
  if (!panels) return [];
  return panels
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
