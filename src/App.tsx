//import React, { useState } from "react";
import Sidebar from "./components/Sidebar/Sidebar";
import Dashboard from "./pages/Dashboard/Dashboard";
import Processos from "./pages/Processos/Processos";
import Drivers from "./pages/Drivers/Drivers";
import Configuracoes from "./pages/Configuracoes/Configuracoes";
import { useMetrics } from "./hooks/useMetrics";
import type { Metric } from "./hooks/useMetrics";
import styles from "./App.module.css";
import { useState } from "react";

export default function App() {
  const { metrics, loading, error } = useMetrics(3000);
  const [page, setPage] = useState("dashboard");

  const renderPage = () => {
    switch (page) {
      case "dashboard":
        return <Dashboard metrics={metrics as Metric} />;
      case "processos":
        return <Processos />;
      case "drivers":
        return <Drivers />;
      case "config":
        return <Configuracoes />;
      default:
        return <Dashboard metrics={metrics as Metric} />;
    }
  };

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
      <Sidebar onSelect={setPage} />
      {renderPage()}
    </div>
  );
}
