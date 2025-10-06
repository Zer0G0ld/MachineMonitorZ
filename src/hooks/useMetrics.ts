import { useEffect, useState } from "react";

export interface Metric {
  timestamp: string;
  cpu?: { usage_pct: number[]; physical_cores: number; total_cores: number };
  memory?: { total: number; used: number; used_pct: number };
  disks?: { device: string; used_pct: number }[];
  top_processes?: { name: string; cpu_percent: number }[];
}

export const useMetrics = (pollInterval = 3000) => {
  const [metrics, setMetrics] = useState<Metric | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      const res = await fetch("http://127.0.0.1:17820/metrics");
      const data = await res.json();
      setMetrics(data);
      setError(null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, pollInterval);
    return () => clearInterval(interval);
  }, [pollInterval]);

  return { metrics, loading, error };
};
