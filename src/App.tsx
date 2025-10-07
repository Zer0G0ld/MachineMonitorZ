import React from "react";
import Sidebar from "./components/Sidebar/Sidebar";
import Dashboard from "./components/Dashboard/Dashboard";
import { useMetrics } from "./hooks/useMetrics";
import type { Metric } from "./hooks/useMetrics";
import styles from "./App.module.css";

export default function App() {
  const { metrics, loading, error } = useMetrics(3000);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p>Carregando métricas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <p className={styles.errorText}>Erro ao carregar métricas</p>
        <p className={styles.errorDetails}>{error}</p>
      </div>
    );
  }

  return (
  <div className={styles.app}>
    <Sidebar />
    <Dashboard metrics={metrics as Metric} />
  </div>
);

}
