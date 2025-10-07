# modulos/logger_setup.py
import logging
import sys
import os

# Mapeia o LogLevel do agent.conf para o logging do Python
LOG_LEVEL_MAP = {
    0: logging.INFO,       # informações básicas
    1: logging.CRITICAL,   # crítico
    2: logging.ERROR,      # erros
    3: logging.WARNING,    # avisos
    4: logging.DEBUG,      # debug
    5: logging.DEBUG       # debug detalhado (ou logging.NOTSET se quiser extremo)
}

def setup_logger(name="agent", log_type="file", log_file="./agent.log", log_level=3):
    """
    Configura um logger para o agent.
    
    :param name: nome do logger
    :param log_type: 'file' para salvar no arquivo, 'console' apenas no stdout
    :param log_file: caminho do arquivo de log
    :param log_level: nível do log (0 a 5)
    :return: objeto logger configurado
    """
    logger = logging.getLogger(name)
    # Remove handlers antigos para não duplicar logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Converte nível do conf para logging
    level = LOG_LEVEL_MAP.get(log_level, logging.WARNING)
    logger.setLevel(level)
    
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    # Console handler sempre disponível
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    
    # File handler se LogType=file
    if log_type.lower() == "file":
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    
    return logger
