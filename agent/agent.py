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
import json
import threading
import platform
import subprocess
import shutil
from datetime import datetime
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


# Config
HOST = "127.0.0.1"
PORT = 8000
POLL_INTERVAL = 3           # segundos entre coletas
PUSH_URL = None             # se setado, agente fará POST para esse URL com os dados
AUTO_ELEVATE = True         # tentar pedir privilégio na 1a execução

# Estado
latest_metrics = {}
latest_lock = threading.Lock()

def is_windows():
    return platform.system().lower() == "windows"

def ensure_admin():
    """Tenta elevar privilégios no Windows (ShellExecute runas) ou chama pkexec/sudo no Linux."""
    if not AUTO_ELEVATE:
        return
    try:
        if is_windows():
            # Windows: relança com RunAs se não for admin
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                return
            print("Reiniciando com privilégios administrativos...")
            params = " ".join([f'"{p}"' for p in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit(0)
        else:
            # Linux/macOS
            if os.geteuid() == 0:
                return
            # Tenta pkexec, senão sudo (pode pedir senha)
            if shutil.which("pkexec"):
                print("Tentando elevar com pkexec...")
                os.execvp("pkexec", ["pkexec", sys.executable] + sys.argv)
            else:
                print("Tentando elevar com sudo (poderá pedir senha)...")
                os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
    except Exception as e:
        print("Elevação falhou ou foi cancelada:", e)
        # Continua sem admin — muitas coisas ainda funcionam

def get_basic_hw_info():
    info = {}
    try:
        uname = platform.uname()
        info["system"] = uname.system
        info["node"] = uname.node
        info["release"] = uname.release
        info["version"] = uname.version
        info["machine"] = uname.machine
        info["processor"] = uname.processor
    except Exception:
        pass

    # Tentativa de obter modelo em Windows via WMI
    if is_windows():
        try:
            import wmi
            c = wmi.WMI()
            cs = c.Win32_ComputerSystem()[0]
            info["manufacturer"] = cs.Manufacturer
            info["model"] = cs.Model
        except Exception:
            pass
    else:
        # Linux: tentar /sys/devices/virtual/dmi/id/*
        try:
            def read_file(path):
                if os.path.exists(path):
                    with open(path, "r", errors="ignore") as f:
                        return f.read().strip()
                return None
            info["manufacturer"] = read_file("/sys/devices/virtual/dmi/id/sys_vendor")
            info["model"] = read_file("/sys/devices/virtual/dmi/id/product_name")
        except Exception:
            pass
    return info

def collect_metrics():
    """Coleta um dicionário com as métricas principais."""
    m = {}
    try:
        m["timestamp"] = datetime.utcnow().isoformat() + "Z"
        # hardware básico
        m["hw"] = get_basic_hw_info()

        # CPU
        m["cpu"] = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "usage_pct": psutil.cpu_percent(interval=None)
        }
        # Memory
        vm = psutil.virtual_memory()
        m["memory"] = {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "used_pct": vm.percent
        }
        # Swap
        sw = psutil.swap_memory()
        m["swap"] = {"total": sw.total, "used": sw.used, "free": sw.free, "used_pct": sw.percent}

        # Disk
        disks = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "used_pct": usage.percent
                })
            except Exception:
                continue
        m["disks"] = disks

        # Network
        net_io = psutil.net_io_counters(pernic=False)
        m["network"] = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }

        # Processes: top 5 by cpu
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "username"]):
            try:
                procs.append(p.info)
            except Exception:
                continue
        procs_sorted = sorted(procs, key=lambda x: x.get("cpu_percent") or 0, reverse=True)[:8]
        m["top_processes"] = procs_sorted

        # Drivers / kernel modules (informação básica)
        drivers = []
        if is_windows():
            # usar driverquery
            try:
                out = subprocess.check_output(["driverquery", "/FO", "CSV"], universal_newlines=True, stderr=subprocess.DEVNULL)
                # devolve número de linhas como resumo, e não parse completo (por performance)
                drivers = {"summary_lines": out.count("\n")}
            except Exception:
                drivers = {"error": "driverquery_failed"}
        else:
            # Linux: lsmod
            try:
                out = subprocess.check_output(["lsmod"], universal_newlines=True, stderr=subprocess.DEVNULL)
                drivers = {"summary_lines": out.count("\n")}
            except Exception:
                drivers = {"error": "lsmod_failed"}
        m["drivers"] = drivers

        # IP / connectivity basic test (dns resolution and ping google)
        try:
            addrs = psutil.net_if_addrs()
            m["interfaces"] = {k: [str(x.address) for x in v if hasattr(x, "address")] for k, v in addrs.items()}
        except Exception:
            m["interfaces"] = {}

    except Exception as e:
        m["error"] = str(e)
    return m

def background_collector():
    """Roda em loop coletando métricas e guardando em latest_metrics; opcionalmente faz POST para PUSH_URL."""
    global latest_metrics
    while True:
        m = collect_metrics()
        with latest_lock:
            latest_metrics = m
        if PUSH_URL:
            try:
                requests.post(PUSH_URL, json=m, timeout=5)
            except Exception as e:
                # falha no envio não para o agente
                print("Falha ao enviar push:", e)
        time.sleep(POLL_INTERVAL)

# Flask app que expõe o estado atual
app = Flask("agent_api")
CORS(app)  # permite qualquer origem

@app.route("/metrics", methods=["GET"])
def get_metrics():
    with latest_lock:
        return jsonify(latest_metrics or {"status": "empty"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "ts": datetime.utcnow().isoformat() + "Z"})

@app.route("/config", methods=["POST"])
def set_config():
    """
    Endpoint simples para ajustar config em runtime.
    Ex.: POST {"poll_interval":5, "push_url":"http://..."}
    """
    global POLL_INTERVAL, PUSH_URL
    data = request.json or {}
    if "poll_interval" in data:
        try:
            val = int(data["poll_interval"])
            POLL_INTERVAL = max(1, val)
        except:
            pass
    if "push_url" in data:
        PUSH_URL = data["push_url"]
    return jsonify({"ok": True, "poll_interval": POLL_INTERVAL, "push_url": PUSH_URL})

def start_flask_app():
    # roda flask numa thread separada
    app.run(host=HOST, port=PORT, threaded=True)

def main():
    # opcional: elevar privilégios se necessário
    try:
        ensure_admin()
    except Exception:
        pass

    # start collector thread
    t = threading.Thread(target=background_collector, daemon=True)
    t.start()

    # start flask (blocking)
    start_flask_app()

if __name__ == "__main__":
    main()