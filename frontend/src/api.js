const API_URL = import.meta.env.VITE_API_URL || "";

function getToken() {
  return localStorage.getItem("eve_token");
}

export async function api(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : detail || "Request failed";
    throw new Error(message);
  }
  return data;
}

export const AuthAPI = {
  signup: (payload) => api("/auth/signup", { method: "POST", body: payload }),
  login: (payload) => api("/auth/login", { method: "POST", body: payload }),
};

export const CentreAPI = {
  list: (params = {}) => {
    const query = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, value]) => value))
    );
    const suffix = query.toString() ? `?${query}` : "";
    return api(`/centres/${suffix}`);
  },
  get: (id) => api(`/centres/${id}`),
  tests: (id) => api(`/centres/${id}/tests`),
  categories: () => api("/centres/categories"),
  cities: () => api("/centres/meta/cities"),
};

export const TestAPI = {
  get: (id) => api(`/tests/${id}`),
};

export const BookingAPI = {
  create: (payload) => api("/bookings/", { method: "POST", body: payload, auth: true }),
  list: () => api("/bookings/", { auth: true }),
  get: (id) => api(`/bookings/${id}`, { auth: true }),
  cancel: (id) => api(`/bookings/${id}/cancel`, { method: "PATCH", auth: true }),
};

export const PaymentAPI = {
  create: (payload) => api("/payments/", { method: "POST", body: payload, auth: true }),
};
