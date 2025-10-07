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
import sys
import threading

from modulos.config_loader import load_config
from modulos.process_details import get_process_details
from modulos.utils import ensure_admin
from modulos.config_loader import load_config
from modulos.logger_setup import setup_logger
from modulos.collect_metrics import background_collector

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

config = load_config("agent.conf")

HOST = config.get("ListenHost", "127.0.0.1")
PORT = config.get("ListenPort", 17820)
POLL_INTERVAL = config.get("PollInterval", 3)
PUSH_URL = config.get("PushURL", None)
AUTO_ELEVATE = config.get("AutoElevate", True)
CPU_ALERT_THRESHOLD = config.get("CPUAlertThreshold", 90)
MEM_ALERT_THRESHOLD = config.get("MemoryAlertThreshold", 90)
TOP_PROCESS_COUNT = config.get("TopProcessCount", 8)

logger = setup_logger(log_level=config.get("LogLevel", 3))

# ============================
# MAIN
# ============================
def main():
    logger.info("Iniciando agent...")
    
    # Elevação de privilégios
    try:
        ensure_admin(AUTO_ELEVATE)
        logger.info("Elevação de privilégios concluída.")
    except Exception:
        logger.warning("Elevação de privilégios falhou ou cancelada. Continuando com privilégios normais.")

    # Estado compartilhado
    latest_metrics = {}
    latest_lock = threading.Lock()
    poll_interval_ref = [POLL_INTERVAL]
    push_url_ref = [PUSH_URL]

    # Coletor em background
    t = threading.Thread(target=background_collector, args=(latest_metrics, latest_lock), kwargs={
        "poll_interval": poll_interval_ref[0],
        "push_url": push_url_ref[0],
        "logger": logger,
        "cpu_alert_threshold": CPU_ALERT_THRESHOLD,
        "mem_alert_threshold": MEM_ALERT_THRESHOLD,
        "top_process_count": TOP_PROCESS_COUNT
    }, daemon=True)
    t.start()
    logger.info(f"Coletor iniciado. Poll interval: {poll_interval_ref[0]} segundos.")

    # Flask API
    from modulos.api import create_app
    app = create_app(latest_metrics, latest_lock, get_process_details, logger, poll_interval_ref, push_url_ref)
    logger.info(f"Flask HTTP rodando em http://{HOST}:{PORT}/")
    app.run(host=HOST, port=PORT, threaded=True)

if __name__ == "__main__":
    main()