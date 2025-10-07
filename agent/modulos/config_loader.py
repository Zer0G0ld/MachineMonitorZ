# modulos/config_loader.py
import os

def load_config(path):
    """
    Lê um arquivo de configuração estilo chave=valor
    e retorna um dicionário.
    Comentários (#) e linhas vazias são ignorados.
    """
    config = {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignora linhas vazias ou comentários
            if not line or line.startswith("#"):
                continue
            # Chave=Valor
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Conversões básicas
                if value.lower() in ("true", "yes", "on"):
                    value = True
                elif value.lower() in ("false", "no", "off"):
                    value = False
                else:
                    try:
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass  # deixa como string
                config[key] = value
    return config
