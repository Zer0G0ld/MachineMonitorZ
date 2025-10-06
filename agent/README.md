# MachineMonitorZ Agent

O **Agent** é responsável por coletar informações do sistema e enviar para o frontend via HTTP.  

### Funcionalidades
- Coleta dados de CPU, memória, disco, rede, processos e drivers
- Executa em background
- Requer permissão de administrador apenas uma vez
- Suporta envio de dados para frontend local ou remoto

### Estrutura
```bash
agent/
├── agent.py          # Código principal do agente
├── requirements.txt  # Dependências Python
└── README.md
```

### Requisitos
- Python 3.10+
- Pacotes listados em `requirements.txt`

### Instalação
```bash
cd agent
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Importante
Note que a porta padrao e 17820

### Uso

```bash
python .\agent.py # Windows
python3 agent.py # linux
```

O agente começará a coletar métricas e enviá-las para o frontend no endereço configurado no código.

### Configuração

* Endereço do frontend pode ser configurado dentro do `agent.py`.
* Permissão de administrador é solicitada na primeira execução.
