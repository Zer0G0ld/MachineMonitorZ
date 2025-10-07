import psutil
from typing import Dict, Any

def get_process_details(pid: int) -> Dict[str, Any]:
    """
    Retorna informações detalhadas de um processo específico.
    Coleta pesada (IO, arquivos, conexões) apenas on-demand.
    """
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            info = {
                "pid": pid,
                "name": p.name(),
                "status": p.status(),
                "cpu_percent": p.cpu_percent(interval=None),  # Instantâneo, sem pausa
                "memory_info": p.memory_info()._asdict(),
                "memory_percent": p.memory_percent(),
                "threads": p.num_threads(),
                "username": p.username(),
            }

            # Coleta mais pesada: IO, arquivos abertos e conexões
            try:
                io = p.io_counters()
                info["io_counters"] = io._asdict() if io else {}
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["io_counters"] = {}

            try:
                info["open_files"] = [f.path for f in p.open_files()]
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["open_files"] = []

            try:
                info["connections"] = [c._asdict() for c in p.connections()]
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                info["connections"] = []

        return info

    except psutil.NoSuchProcess:
        return {"pid": pid, "error": "processo não existe"}
    except psutil.AccessDenied:
        return {"pid": pid, "error": "acesso negado"}
    except Exception as e:
        return {"pid": pid, "error": str(e)}
