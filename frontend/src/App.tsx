import { Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";

import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Transactions from "./pages/Transactions";
import FincasHub from "./pages/FincasHub";
import FincasKakeibo from "./pages/FincasKakeibo";
import FincasMicroSavings from "./pages/FincasMicroSavings";
import FincasLagom from "./pages/FincasLagom";
import FincasMetodos from "./pages/FincasMetodos";
import Planos from "./pages/Planos";
import { TrialBanner } from "./components/TrialBanner";
import { Sidebar } from "./components/Sidebar";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { cn } from "./lib/utils";

function AppLayout({ children, showTrialBanner }: { children: React.ReactNode; showTrialBanner?: boolean }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar open={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <main
        className={cn(
          "flex-1 overflow-y-auto bg-muted/30 p-6 transition-all duration-200",
          sidebarOpen ? "ml-64" : "ml-16"
        )}
      >
        {showTrialBanner !== false && <TrialBanner />}
        {children}
      </main>
    </div>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;
  return <AppLayout>{children}</AppLayout>;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/transactions"
          element={
            <ProtectedRoute>
              <Transactions />
            </ProtectedRoute>
          }
        />
        <Route
          path="/fincas"
          element={
            <ProtectedRoute>
              <FincasHub />
            </ProtectedRoute>
          }
        />
        <Route
          path="/fincas/kakeibo"
          element={
            <ProtectedRoute>
              <FincasKakeibo />
            </ProtectedRoute>
          }
        />
        <Route
          path="/fincas/micro-savings"
          element={
            <ProtectedRoute>
              <FincasMicroSavings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/fincas/lagom"
          element={
            <ProtectedRoute>
              <FincasLagom />
            </ProtectedRoute>
          }
        />
        <Route
          path="/fincas/metodos"
          element={
            <ProtectedRoute>
              <FincasMetodos />
            </ProtectedRoute>
          }
        />
        <Route
          path="/planos"
          element={
            <ProtectedRoute>
              <Planos />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
