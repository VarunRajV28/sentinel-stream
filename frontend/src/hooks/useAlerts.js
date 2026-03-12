import { useEffect, useRef, useState, useCallback } from "react";

export function useAlerts(maxAlerts = 50) {
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const retryDelay = useRef(1000);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/alerts`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      retryDelay.current = 1000;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "ALERT") {
          setAlerts((prev) => [data, ...prev].slice(0, maxAlerts));
        }
      } catch {
        // ignore non-JSON frames
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      if (mountedRef.current) {
        setTimeout(() => {
          retryDelay.current = Math.min(retryDelay.current * 2, 30000);
          connect();
        }, retryDelay.current);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [maxAlerts]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      wsRef.current?.close();
    };
  }, [connect]);

  return { alerts, isConnected };
}
