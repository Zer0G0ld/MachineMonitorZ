import React, { useEffect, useState } from "react";

function prettyBytes(n) {
  if (!n && n !== 0) return "-";
  const units = ["B","KB","MB","GB","TB"];
  let i = 0;
  let val = n;
  while (val >= 1024 && i < units.length-1) { val /= 1024; i++; }
  return `${val.toFixed(1)} ${units[i]}`;
}

export default function App() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function fetchMetrics() {
      try {
        const res = await fetch("http://127.0.0.1:8000/metrics", {cache: "no-store"});
        if (!res.ok) throw new Error("HTTP " + res.status);
        const json = await res.json();
        if (mounted) setMetrics(json);
      } catch (e) {
        if (mounted) setError(e.message);
      }
    }
    fetchMetrics();
    const iv = setInterval(fetchMetrics, 2000);
    return () => { mounted = false; clearInterval(iv); };
  }, []);

  if (error) return <div style={{padding:20}}>Erro conectando ao agent: {error}</div>;
  if (!metrics || Object.keys(metrics).length === 0) return <div style={{padding:20}}>Aguardando dados do agent...</div>;

  return (
    <div style={{padding:20, fontFamily:"Inter, Arial"}}>
      <h2>Monitor da Máquina (local)</h2>
      <div>Última atualização: {metrics.timestamp}</div>

      <section style={{marginTop:12}}>
        <h3>Hardware</h3>
        <pre>{JSON.stringify(metrics.hw, null, 2)}</pre>
      </section>

      <section>
        <h3>CPU</h3>
        <div>Uso: {metrics.cpu?.usage_pct ?? "-"}%</div>
        <div>Cores físicos: {metrics.cpu?.physical_cores}</div>
      </section>

      <section>
        <h3>Memória</h3>
        <div>Total: {prettyBytes(metrics.memory?.total)}</div>
        <div>Usada: {prettyBytes(metrics.memory?.used)} ({metrics.memory?.used_pct}%)</div>
      </section>

      <section>
        <h3>Discos</h3>
        {metrics.disks?.map(d => (
          <div key={d.mountpoint}>
            {d.device} @ {d.mountpoint} — {prettyBytes(d.total)} total — {d.used_pct}% usado
          </div>
        ))}
      </section>

      <section>
        <h3>Top processos</h3>
        <ul>
          {metrics.top_processes?.map(p => (
            <li key={p.pid || Math.random()}>
              {p.name} (pid {p.pid}) — CPU {p.cpu_percent}% — MEM {p.memory_percent?.toFixed?.(1) || "-"}%
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Drivers / Kernel</h3>
        <pre>{JSON.stringify(metrics.drivers || {}, null, 2)}</pre>
      </section>
    </div>
  );
}
