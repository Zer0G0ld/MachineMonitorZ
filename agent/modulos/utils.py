# modulos/utils.py
import os
import sys
import platform
import ctypes
import shutil
import logging

logger = logging.getLogger("agent")

# ---------------------------
# PRIVILEGIOS / ELEVATION
# ---------------------------

def is_windows() -> bool:
    return platform.system().lower() == "windows"

def is_admin() -> bool:
    """
    Retorna True se o script está rodando com privilégios de admin/root
    """
    try:
        if is_windows():
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def ensure_admin(auto_elevate: bool = True):
    """
    Garante privilégios de admin/root.
    Se auto_elevate=False, ignora.
    """
    if not auto_elevate:
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
