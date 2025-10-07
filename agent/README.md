# MachineMonitorZ Agent

O **Agent** é responsável por **coletar informações do sistema** e disponibilizá-las para o frontend via HTTP, além de permitir envio remoto opcional.

### Funcionalidades

* Coleta dados de CPU, memória, disco, rede, processos e drivers
* Coleta em **background** de forma contínua
* Suporte a envio de métricas via HTTP para frontend local ou remoto
* Requer permissão de administrador apenas **uma vez**
* Modularizado para fácil manutenção e extensão
* Logging centralizado com níveis configuráveis

### Estrutura do Projeto

```bash
agent/
├── agent.conf              # Arquivo de configuração do agent (intervalo, porta, alertas, etc.)
├── agent.d                 # Diretório para arquivos auxiliares, scripts ou backups do agent
├── agent.log               # Arquivo de log gerado pelo agent (logging centralizado)
├── agent.py                # Entrypoint principal: inicia coletor e API Flask
├── modulos/                # Módulos Python com funcionalidades do agent
│   ├── api.py              # Criação e roteamento da API Flask (endpoints /metrics, /health, /process)
│   ├── collect_metrics.py  # Funções de coleta de métricas do sistema (CPU, Memória, Disco, Rede, Drivers)
│   ├── config_loader.py    # Carregamento e parsing do arquivo de configuração agent.conf
│   ├── __init__.py         # Torna a pasta um pacote Python
│   ├── logger_setup.py     # Configuração central de logging, respeitando LogLevel
│   ├── process_details.py  # Coleta de informações detalhadas de processos individuais
│   ├── utils.py            # Funções auxiliares: checagem de administrador, helpers OS
│   └── __pycache__/        # Arquivos compilados Python (.pyc) gerados automaticamente
├── README.md               # Documentação do projeto
└── requirements.txt        # Lista de dependências do Python
```

* **Arquivos principais**: `agent.py` é o entrypoint, `agent.conf` configura o comportamento, `requirements.txt` lista dependências.
* **Módulos**: Tudo relacionado à coleta de métricas, logging, API e utils está dentro da pasta `modulos/`.
* **Logs**: `agent.log` armazena todos os logs gerados pelo agent durante execução.

### Requisitos

* Python 3.10+
* Pacotes listados em `requirements.txt`:

  ```text
  psutil
  requests
  flask
  flask-cors
  wmi   # opcional para Windows
  ```

### Instalação

```bash
cd agent
python -m venv venv
# Ativação do ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
# Instalação das dependências
pip install -r requirements.txt
```

### Configuração

Todas as opções podem ser definidas no arquivo `agent.conf`:

```ini
# Endereço do Flask API
ListenHost=127.0.0.1
ListenPort=17820

# Intervalo de coleta em segundos
PollInterval=3

# URL opcional para envio remoto das métricas
PushURL=

# Elevar privilégios automaticamente (True/False)
AutoElevate=True

# Alertas de CPU e Memória em %
CPUAlertThreshold=90
MemoryAlertThreshold=90

# Número de processos top por CPU
TopProcessCount=8

# Nível de log
# 0 - Start/Stop
# 1 - Crítico
# 2 - Erros
# 3 - Avisos (default)
# 4 - Debug
# 5 - Debug detalhado
LogLevel=3
```

### Uso

```bash
python agent.py      # Windows
python3 agent.py     # Linux/Mac
```

* O agente iniciará a **coleta em background**.
* A **API Flask** será iniciada automaticamente, disponível em `http://<HOST>:<PORT>/`.
* Endpoints disponíveis:

  * `/metrics` → Retorna as métricas mais recentes
  * `/health` → Status do agent
  * `/process/<pid>` → Informações detalhadas de um processo específico
  * `/config` → Alteração de `poll_interval` e `push_url` via POST

### Logging

* Centralizado no módulo `logger_setup.py`
* Pode ser configurado via `LogLevel` no `agent.conf`
* Logs são exibidos no console e podem ser redirecionados para arquivo se desejado

### Observações

* A primeira execução pedirá **elevação de privilégios** no Windows ou Linux.
* O agente é modular, permitindo fácil extensão (ex: adicionar novas métricas ou endpoints API).
* Poll interval e PUSH_URL podem ser alterados **dinamicamente via endpoint `/config`**.
