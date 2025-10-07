import { useEffect, useState } from "react";

// Tipagem dos processos detalhados
export interface ProcessDetail {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
  status?: string;
  threads?: number;
  io_counters?: Record<string, number>;
  username?: string;
  open_files?: string[];
  connections?: Record<string, unknown>[];
  error?: string;
}

// Tipagem geral das métricas
export interface Metric {
  timestamp: string;
  cpu?: { usage_pct: number[]; physical_cores: number; total_cores: number };
  memory?: { total: number; used: number; used_pct: number };
  disks?: { device: string; used_pct: number }[];
  top_processes?: ProcessDetail[];
  network?: { bytes_sent: number; bytes_recv: number; packets_sent: number; packets_recv: number };
  drivers?: unknown;
}

export const useMetrics = (pollInterval = 3000) => {
  const [metrics, setMetrics] = useState<Metric | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      const res = await fetch("http://127.0.0.1:17820/metrics");
      const data: Metric = await res.json();
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
