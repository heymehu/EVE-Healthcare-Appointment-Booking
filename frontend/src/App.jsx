import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./pages/HomePage";
import SignupPage from "./pages/SignupPage";
import LoginPage from "./pages/LoginPage";
import CentresPage from "./pages/CentresPage";
import CentreDetailPage from "./pages/CentreDetailPage";
import ServicePage from "./pages/ServicePage";
import BookTestPage from "./pages/BookTestPage";
import PaymentPage, { PaymentResultPage } from "./pages/PaymentPage";
import BookingsPage from "./pages/BookingsPage";
import BookingDetailPage from "./pages/BookingDetailPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/centres" element={<CentresPage />} />
          <Route path="/centres/:centreId" element={<CentreDetailPage />} />
          <Route path="/services/:category" element={<ServicePage />} />
          <Route
            path="/book/:centreId/:testId"
            element={<ProtectedRoute><BookTestPage /></ProtectedRoute>}
          />
          <Route
            path="/payment/success/:bookingId"
            element={<ProtectedRoute><PaymentResultPage kind="success" /></ProtectedRoute>}
          />
          <Route
            path="/payment/failed/:bookingId"
            element={<ProtectedRoute><PaymentResultPage kind="failed" /></ProtectedRoute>}
          />
          <Route
            path="/payment/:bookingId"
            element={<ProtectedRoute><PaymentPage /></ProtectedRoute>}
          />
          <Route
            path="/bookings"
            element={<ProtectedRoute><BookingsPage /></ProtectedRoute>}
          />
          <Route
            path="/bookings/:bookingId"
            element={<ProtectedRoute><BookingDetailPage /></ProtectedRoute>}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
