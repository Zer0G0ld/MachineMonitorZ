import React, { useEffect, useState } from "react";

function prettyBytes(n: number | undefined) {
  if (n === undefined || n === null) return "-";
  const units = ["B","KB","MB","GB","TB"];
  let i = 0;
  let val = n;
  while (val >= 1024 && i < units.length-1) { val /= 1024; i++; }
  return `${val.toFixed(1)} ${units[i]}`;
}

function ProgressBar({value, max=100}: {value:number, max?:number}) {
  const pct = Math.min(Math.max((value/max)*100, 0), 100);
  return (
    <div style={{background:"#eee", width:"100%", height:10, borderRadius:5, marginTop:4}}>
      <div style={{
        width:`${pct}%`,
        height:"100%",
        background: pct>80 ? "red" : "#4caf50",
        borderRadius:5,
        transition:"width 0.3s"
      }} />
    </div>
  );
}

export default function App() {
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function fetchMetrics() {
      try {
        const res = await fetch("http://127.0.0.1:17820/metrics", {cache: "no-store"});
        if (!res.ok) throw new Error("HTTP " + res.status);
        const json = await res.json();
        if (mounted) setMetrics(json);
      } catch (e: any) {
        if (mounted) setError(e.message);
      }
    }
    fetchMetrics();
    const iv = setInterval(fetchMetrics, 2000);
    return () => { mounted = false; clearInterval(iv); };
  }, []);

  if (error) return <div style={{padding:20}}>Erro conectando ao agent: {error}</div>;
  if (!metrics || Object.keys(metrics).length === 0) return <div style={{padding:20}}>Aguardando dados do agent...</div>;

  const cpuAvg = metrics.cpu ? (metrics.cpu.usage_pct.reduce((a:number,b:number)=>a+b,0)/metrics.cpu.usage_pct.length) : 0;

  return (
    <div style={{padding:20, fontFamily:"Inter, Arial", maxWidth:800, margin:"0 auto"}}>
      <h2>Monitor da Máquina (local)</h2>
      <div>Última atualização: {metrics.timestamp}</div>

      {/* Hardware */}
      <section style={{padding:10, marginTop:12, border:"1px solid #ccc", borderRadius:6, background:"#fafafa"}}>
        <h3>Hardware</h3>
        <pre>{JSON.stringify(metrics.hw, null, 2)}</pre>
      </section>

      {/* CPU */}
      <section style={{padding:10, marginTop:12, border:"1px solid #ccc", borderRadius:6, background:"#fafafa"}}>
        <h3>CPU</h3>
        <div>Cores físicos: {metrics.cpu?.physical_cores}</div>
        <div>Uso médio: {cpuAvg.toFixed(1)}%</div>
        <ProgressBar value={cpuAvg}/>
      </section>

      {/* Memória */}
      <section style={{padding:10, marginTop:12, border:"1px solid #ccc", borderRadius:6, background:"#fafafa"}}>
        <h3>Memória</h3>
        <div>Total: {prettyBytes(metrics.memory?.total)}</div>
        <div>Usada: {prettyBytes(metrics.memory?.used)} ({metrics.memory?.used_pct?.toFixed(1)}%)</div>
        <ProgressBar value={metrics.memory?.used_pct || 0}/>
      </section>

      {/* Discos */}
      <section style={{padding:10, marginTop:12, border:"1px solid #ccc", borderRadius:6, background:"#fafafa"}}>
        <h3>Discos</h3>
        {metrics.disks?.map((d:any) => (
          <div key={d.mountpoint} style={{marginBottom:6}}>
            <strong>{d.device} @ {d.mountpoint}</strong> — {prettyBytes(d.used)} / {prettyBytes(d.total)} ({d.used_pct}%)
            <ProgressBar value={d.used_pct}/>
          </div>
        ))}
      </section>

      {/* Top Processes */}
      <section style={{padding:10, marginTop:12, border:"1px solid #ccc", borderRadius:6, background:"#fafafa"}}>
        <h3>Top Processes (CPU)</h3>
        <ul>
          {metrics.top_processes?.slice(0,5).map((p:any) => (
            <li key={p.pid || Math.random()}>
              {p.name} (pid {p.pid}) — CPU {p.cpu_percent}% — MEM {p.memory_percent?.toFixed?.(1) || "-"}%
            </li>
          ))}
        </ul>
      </section>

      {/* Drivers / Kernel */}
      <section style={{padding:10, marginTop:12, border:"1px solid #ccc", borderRadius:6, background:"#fafafa"}}>
        <h3>Drivers / Kernel</h3>
        <pre>{JSON.stringify(metrics.drivers || {}, null, 2)}</pre>
      </section>
    </div>
  );
}
