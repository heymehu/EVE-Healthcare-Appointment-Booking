import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

function apiProxy(target) {
  return {
    target,
    bypass(req) {
      // Keep React routes on refresh; only proxy XHR/fetch to FastAPI.
      if (req.headers.accept?.includes("text/html")) {
        return "/index.html";
      }
    },
  };
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/auth": apiProxy("http://localhost:8000"),
      "/centres": apiProxy("http://localhost:8000"),
      "/tests": apiProxy("http://localhost:8000"),
      "/bookings": apiProxy("http://localhost:8000"),
      "/payments": apiProxy("http://localhost:8000"),
      "/health": apiProxy("http://localhost:8000"),
    },
  },
});
