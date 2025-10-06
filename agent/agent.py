#!/usr/bin/env python3
"""
Agent de monitoramento local.
- Coleta: modelo, CPU, memória, disco, rede, processos, drivers (informações básicas).
- Pede elevação (Windows/Linux) na primeira execução.
- Roda coleta periódica em background.
- Expõe HTTP local em http://127.0.0.1:8000/metrics para o frontend consultar (poll).
- Opcional: configura PUSH_URL para enviar via POST os dados (push).
Dependências: psutil, requests, flask, wmi (somente Windows, opcional).
Instalação:
    pip install psutil requests flask
    pip install wmi         # opcional, para info de hardware no Windows
"""
import os
import sys
import time
import threading
import platform
import ctypes
import subprocess
import logging
import shutil
from datetime import datetime, timezone
from flask_cors import CORS
from flask import Flask, jsonify, request

try:
    import psutil
except ImportError:
    print("psutil não instalado. Rode: pip install psutil")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("requests não instalado. Rode: pip install requests")
    sys.exit(1)

# ============================
# CONFIG
# ============================
HOST = "127.0.0.1"
PORT = 17820
POLL_INTERVAL = 3
PUSH_URL = None
AUTO_ELEVATE = True

# Thresholds de alerta
CPU_ALERT_THRESHOLD = 90
MEM_ALERT_THRESHOLD = 90

# Logging
logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)
fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setFormatter(fmt)
logger.addHandler(ch)

# Suprime logs verbose do Flask/Werkzeug
flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.ERROR)

# Estado
latest_metrics = {}
latest_lock = threading.Lock()

# ============================
# PRIVILEGIOS
# ============================
def is_windows() -> bool:
    return platform.system().lower() == "windows"

def is_admin() -> bool:
    try:
        if is_windows():
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def ensure_admin():
    if not AUTO_ELEVATE:
        return
    try:
        if is_admin():
            return
        if is_windows():
            logger.info("Solicitando elevação de privilégios (UAC)...")
            params = " ".join([f'"{p}"' for p in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit(0)
        else:
            if shutil.which("pkexec"):
                logger.info("Tentando elevar com pkexec...")
                os.execvp("pkexec", ["pkexec", sys.executable] + sys.argv)
            else:
                logger.info("Tentando elevar com sudo (poderá pedir senha)...")
                os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
    except Exception as e:
        logger.warning(f"Elevação falhou ou foi cancelada: {e}")

# ============================
# MÉTRICAS
# ============================
def get_basic_hw_info():
    info = {}
    try:
        uname = platform.uname()
        info.update({
            "system": uname.system,
            "node": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor
        })
    except Exception:
        pass

    if is_windows():
        try:
            import wmi
            c = wmi.WMI()
            cs = c.Win32_ComputerSystem()[0]
            info.update({"manufacturer": cs.Manufacturer, "model": cs.Model})
        except ImportError:
            info.update({"manufacturer": None, "model": None})
            logger.warning("wmi não instalado. Rode: pip install wmi")
        except Exception:
            info.update({"manufacturer": None, "model": None})
    else:
        def read_file(path):
            if os.path.exists(path):
                with open(path, "r", errors="ignore") as f:
                    return f.read().strip()
            return None
        info.update({
            "manufacturer": read_file("/sys/devices/virtual/dmi/id/sys_vendor"),
            "model": read_file("/sys/devices/virtual/dmi/id/product_name")
        })
    return info

def collect_metrics():
    m = {}
    try:
        m["timestamp"] = datetime.now(timezone.utc).isoformat()
        m["hw"] = get_basic_hw_info()

        # CPU
        cpu_percents = psutil.cpu_percent(percpu=True)
        m["cpu"] = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "usage_pct": cpu_percents
        }
        cpu_avg = sum(cpu_percents) / len(cpu_percents)

        # Memória
        vm = psutil.virtual_memory()
        mem_used_pct = vm.percent
        m["memory"] = {"total": vm.total, "available": vm.available, "used": vm.used, "used_pct": mem_used_pct}

        sw = psutil.swap_memory()
        m["swap"] = {"total": sw.total, "used": sw.used, "free": sw.free, "used_pct": sw.percent}

        # Disco
        disks = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({"device": part.device, "mountpoint": part.mountpoint,
                              "fstype": part.fstype, "total": usage.total,
                              "used": usage.used, "free": usage.free,
                              "used_pct": usage.percent})
            except Exception:
                continue
        m["disks"] = disks

        # Rede
        net_io = psutil.net_io_counters(pernic=False)
        m["network"] = {"bytes_sent": net_io.bytes_sent, "bytes_recv": net_io.bytes_recv,
                        "packets_sent": net_io.packets_sent, "packets_recv": net_io.packets_recv}

        # Processos
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "username"]):
            try:
                procs.append(p.info)
            except Exception:
                continue
        top_procs = sorted(procs, key=lambda x: x.get("cpu_percent") or 0, reverse=True)[:8]
        m["top_processes"] = top_procs

        # Drivers
        drivers = []
        if is_windows():
            try:
                out = subprocess.check_output(["driverquery", "/FO", "CSV"], universal_newlines=True, stderr=subprocess.DEVNULL)
                drivers = {"summary_lines": out.count("\n")}
            except Exception:
                drivers = {"error": "driverquery_failed"}
        else:
            try:
                out = subprocess.check_output(["lsmod"], universal_newlines=True, stderr=subprocess.DEVNULL)
                drivers = {"summary_lines": out.count("\n")}
            except Exception:
                drivers = {"error": "lsmod_failed"}
        m["drivers"] = drivers

        try:
            addrs = psutil.net_if_addrs()
            m["interfaces"] = {k: [str(x.address) for x in v if hasattr(x, "address")] for k, v in addrs.items()}
        except Exception:
            m["interfaces"] = {}

    except Exception as e:
        m["error"] = str(e)

    # Logs de métricas resumidas
    disk_summary = ", ".join([f"{d['mountpoint']}:{d['used_pct']}%" for d in disks])
    top_proc_summary = ", ".join([f"{p['name']}({p['cpu_percent']}%)" for p in top_procs])
    logger.info(f"[Metrics] CPU(avg)={cpu_avg:.1f}% MEM={mem_used_pct:.1f}% DISKS={disk_summary} TOPPROC={top_proc_summary}")

    # Alertas
    if cpu_avg > CPU_ALERT_THRESHOLD:
        logger.warning(f"[ALERT] CPU média alta: {cpu_avg:.1f}%")
    if mem_used_pct > MEM_ALERT_THRESHOLD:
        logger.warning(f"[ALERT] MEM usada alta: {mem_used_pct:.1f}%")

    return m

def background_collector():
    global latest_metrics
    while True:
        m = collect_metrics()
        with latest_lock:
            latest_metrics = m
        if PUSH_URL:
            try:
                requests.post(PUSH_URL, json=m, timeout=5)
            except Exception as e:
                logger.warning(f"Falha ao enviar push: {e}")
        time.sleep(POLL_INTERVAL)

# ============================
# FLASK APP
# ============================
app = Flask("agent_api")
CORS(app)

@app.route("/metrics", methods=["GET"])
def get_metrics():
    with latest_lock:
        return jsonify(latest_metrics or {"status": "empty"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "ts": datetime.now(timezone.utc).isoformat()})

@app.route("/config", methods=["POST"])
def set_config():
    global POLL_INTERVAL, PUSH_URL
    data = request.json or {}
    if "poll_interval" in data:
        try:
            val = int(data["poll_interval"])
            POLL_INTERVAL = max(1, val)
            logger.info(f"Poll interval alterado para {POLL_INTERVAL}s")
        except:
            pass
    if "push_url" in data:
        PUSH_URL = data["push_url"]
        logger.info(f"PUSH_URL alterado para {PUSH_URL}")
    return jsonify({"ok": True, "poll_interval": POLL_INTERVAL, "push_url": PUSH_URL})

def start_flask_app():
    logger.info(f"Flask HTTP rodando em http://{HOST}:{PORT}/")
    app.run(host=HOST, port=PORT, threaded=True)

# ============================
# MAIN
# ============================
def main():
    logger.info("Iniciando agent...")
    try:
        ensure_admin()
        logger.info("Elevação de privilégios concluída.")
    except Exception:
        logger.warning("Elevação de privilégios falhou ou cancelada. Continuando com privilégios normais.")

    logger.info("Iniciando coletor de métricas em background...")
    t = threading.Thread(target=background_collector, daemon=True)
    t.start()
    logger.info(f"Coletor iniciado. Poll interval: {POLL_INTERVAL} segundos.")

    start_flask_app()

if __name__ == "__main__":
    main()