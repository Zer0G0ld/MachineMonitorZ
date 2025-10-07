import MetricCard from "../../components/Card/Card";
import type { Metric } from "../../hooks/useMetrics";
import styles from "./Dashboard.module.css";

interface DashboardProps {
  metrics: Metric | null;
}

export default function Dashboard({ metrics }: DashboardProps) {
  const cpu = metrics?.cpu?.usage_pct[0]?.toFixed(1) ?? "0";
  const memory = metrics?.memory?.used_pct?.toFixed(1) ?? "0";
  const disk = metrics?.disks?.[0]?.used_pct?.toFixed(1) ?? "0";

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.headerTitle}>Painel de Monitoramento</h2>
          <p className={styles.headerTimestamp}>
            Atualizado em {new Date(metrics?.timestamp ?? Date.now()).toLocaleTimeString()}
          </p>
        </div>
      </div>

      <div className={styles.separator}></div>

      <div className={styles.cardsGrid}>
        <MetricCard title="CPU" value={`${cpu}%`} color="#3b82f6" />
        <MetricCard title="Memória" value={`${memory}%`} color="#10b981" />
        <MetricCard title="Disco" value={`${disk}%`} color="#f97316" />
      </div>

      <div className={styles.topProcessesSection}>
        <h3 className={styles.topProcessesTitle}>Processos Principais</h3>
        {metrics?.top_processes?.length ? (
          <div className={styles.topProcessesList}>
            {metrics.top_processes.slice(0, 5).map((p, i) => (
              <div className={styles.processItem} key={i}>
                <span className={styles.processName}>{p.name}</span>
                <span className={styles.processCpu}>{p.cpu_percent.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        ) : (
          <p className={styles.noProcesses}>Nenhum processo listado.</p>
        )}
      </div>
    </div>
  );
}
