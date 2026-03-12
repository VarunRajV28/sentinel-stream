import { Routes, Route } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import Dashboard from "./pages/Dashboard";
import Investigate from "./pages/Investigate";
import ErrorBoundary from "./components/ui/ErrorBoundary";
import { useAlerts } from "./hooks/useAlerts";

export default function App() {
  const { alerts, isConnected } = useAlerts();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar isConnected={isConnected} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Dashboard alerts={alerts} />} />
            <Route path="/investigate" element={<Investigate />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  );
}
