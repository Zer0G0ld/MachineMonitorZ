# modulos/collect_metrics.py
import os
import platform
import psutil
import subprocess
import heapq
from datetime import datetime, timezone

def is_windows():
    return platform.system().lower() == "windows"

def get_basic_hw_info(logger=None):
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
            if logger:
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

def collect_metrics(logger=None, cpu_alert_threshold=90, mem_alert_threshold=90, top_process_count=8):
    m = {}
    try:
        m["timestamp"] = datetime.now(timezone.utc).isoformat()
        m["hw"] = get_basic_hw_info(logger=logger)

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
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        top_procs = heapq.nlargest(top_process_count, procs, key=lambda x: x.get("cpu_percent") or 0)
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
    if logger:
        disk_summary = ", ".join([f"{d['mountpoint']}:{d['used_pct']}%" for d in disks])
        top_proc_summary = ", ".join([f"{p['name']}({p['cpu_percent']}%)" for p in top_procs])
        logger.info(f"[Metrics] CPU(avg)={cpu_avg:.1f}% MEM={mem_used_pct:.1f}% DISKS={disk_summary} TOPPROC={top_proc_summary}")

        # Alertas
        if cpu_avg > cpu_alert_threshold:
            logger.warning(f"[ALERT] CPU média alta: {cpu_avg:.1f}%")
        if mem_used_pct > mem_alert_threshold:
            logger.warning(f"[ALERT] MEM usada alta: {mem_used_pct:.1f}%")

    return m

def background_collector(latest_metrics, latest_lock, poll_interval=3, push_url=None, logger=None, cpu_alert_threshold=90, mem_alert_threshold=90, top_process_count=8):
    import time
    import requests

    while True:
        m = collect_metrics(logger=logger, cpu_alert_threshold=cpu_alert_threshold, mem_alert_threshold=mem_alert_threshold, top_process_count=top_process_count)
        with latest_lock:
            latest_metrics.clear()
            latest_metrics.update(m)
        if push_url:
            try:
                requests.post(push_url, json=m, timeout=5)
            except Exception as e:
                if logger:
                    logger.warning(f"Falha ao enviar push: {e}")
        time.sleep(poll_interval)
