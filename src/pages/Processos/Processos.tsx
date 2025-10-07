import { useEffect, useState } from "react";
import { useMetrics } from "../../hooks/useMetrics";
import styles from "./Processos.module.css";

export default function Processos() {
  const { metrics, loading, error } = useMetrics(3000);
  const [processList, setProcessList] = useState<{ name: string; cpu_percent: number }[]>([]);

  useEffect(() => {
    if (metrics?.top_processes) {
      setProcessList(metrics.top_processes);
    }
  }, [metrics]);

  if (loading) return <p className={styles.message}>Carregando processos...</p>;
  if (error) return <p className={styles.messageError}>Erro: {error}</p>;
  if (!processList.length) return <p className={styles.message}>Nenhum processo listado.</p>;

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Processos em Execução</h2>
      <div className={styles.list}>
        {processList.map((proc, idx) => (
          <div key={idx} className={styles.item}>
            <span className={styles.name}>{proc.name}</span>
            <span className={styles.cpu}>{proc.cpu_percent.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
