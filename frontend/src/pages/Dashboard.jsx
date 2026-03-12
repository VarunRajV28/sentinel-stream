import { useState, useEffect } from "react";
import AlertFeed from "../features/dashboard/AlertFeed";
import RevenueChart from "../features/dashboard/RevenueChart";
import WhaleList from "../features/dashboard/WhaleList";
import AuthFunnel from "../features/dashboard/AuthFunnel";
import { fetchWhales, fetchAuth } from "../services/api";

export default function Dashboard({ alerts }) {
  const [whales, setWhales] = useState([]);
  const [authData, setAuthData] = useState(null);

  useEffect(() => {
    async function refreshMetrics() {
      try {
        const [w, a] = await Promise.all([fetchWhales(), fetchAuth()]);
        setWhales(w);
        setAuthData(a);
      } catch (err) {
        console.error("Failed to fetch dashboard metrics:", err);
      }
    }

    refreshMetrics();
    const interval = setInterval(refreshMetrics, 5000); // refresh every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Row 1: Alerts (3/4) & Whales (1/4) */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-stretch">
        <div className="lg:col-span-3 h-full">
          <AlertFeed alerts={alerts} />
        </div>
        <div className="lg:col-span-1 h-full">
          <WhaleList whales={whales} />
        </div>
      </div>

      {/* Row 2: Revenue (1/2) & Auth (1/2) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        <div className="h-full">
          <RevenueChart />
        </div>
        <div className="h-full">
          <AuthFunnel authData={authData} />
        </div>
      </div>
    </div>
  );
}
