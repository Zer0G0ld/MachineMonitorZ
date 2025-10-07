import { useState } from "react";
import styles from "./Processos.module.css";
import type { Metric } from "../../hooks/useMetrics";

interface ConnectionDetail {
  fd?: number;
  family?: number;
  laddr?: Record<string, unknown>;
  raddr?: Record<string, unknown>;
  status?: string;
  type?: number;
}

interface ProcessDetail {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
  status?: string;
  threads?: number;
  io_counters?: Record<string, number | string>;
  username?: string;
  open_files?: string[];
  connections?: ConnectionDetail[];
  error?: string;
}


export default function Processos({ metrics }: { metrics?: Metric }) {
  const [selected, setSelected] = useState<ProcessDetail | null>(null);

  const handleClick = async (pid: number) => {
    const res = await fetch(`http://127.0.0.1:17820/process/${pid}`);
    const data = await res.json();
    setSelected(data);
  };

  return (
    <div className={styles.container}>
      <div className={styles.processTable}>
        <h2>Top Processos</h2>
        <table>
          <thead>
            <tr>
              <th>PID</th>
              <th>Nome</th>
              <th>CPU %</th>
              <th>Mem %</th>
            </tr>
          </thead>
          <tbody>
            {metrics?.top_processes?.map((p) => (
              <tr key={p.pid} onClick={() => handleClick(p.pid)}>
                <td>{p.pid}</td>
                <td>{p.name}</td>
                <td>{p.cpu_percent}</td>
                <td>{p.memory_percent?.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className={styles.detailsSidebar}>
          <h3>{selected.name} (PID: {selected.pid})</h3>
          <p>Status: {selected.status}</p>
          <p>CPU: {selected.cpu_percent}%</p>
          <p>Memória: {selected.memory_percent?.toFixed(2)}%</p>
          <p>Threads: {selected.threads}</p>
          {Array.isArray(selected.open_files) && selected.open_files.length > 0 && (
            <p>Arquivos abertos: {selected.open_files.join(", ")}</p>
          )}

          {selected.io_counters && <p>IO: {JSON.stringify(selected.io_counters)}</p>}
          {selected.connections && <p>Conexões: {JSON.stringify(selected.connections)}</p>}
        </div>
      )}

    </div>
  );
}
