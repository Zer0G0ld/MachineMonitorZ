# MachineMonitorZ

MachineMonitorZ é um sistema de monitoramento de máquinas, que coleta informações de hardware e software (CPU, memória, disco, rede, processos, drivers, etc.) através de um agente Python e exibe em um frontend web moderno (React + Vite).

O projeto é dividido em duas partes:
- **Agent**: coleta métricas do sistema e envia via HTTP.
- **Frontend**: dashboard web que consome os dados do agente e exibe métricas em tempo real.

## Estrutura do projeto

```

MachineMonitorZ/
├── agent/        # Backend/Agente Python
├── src/          # Frontend React + Vite
├── public/       # Arquivos estáticos do frontend
├── package.json  # Dependências e scripts do frontend
└── README.md     # Este arquivo

```

Para mais detalhes, veja os READMEs específicos de cada parte:

- [Agent README](./agent/README.md)

# MachineMonitorZ Frontend(raiz)

O **Frontend** exibe as métricas coletadas pelo agente Python em um dashboard moderno e responsivo.

### Funcionalidades
- Dashboard com CPU, memória, disco, rede e processos
- Componentes reutilizáveis: Card, Dashboard, Sidebar
- Hooks personalizados para consumir métricas
- Atualização em tempo real via polling ou WebSocket (dependendo da implementação)

### Estrutura
````

src/
├── App.tsx
├── components/       # Componentes React
│   ├── Card/
│   ├── Dashboard/
│   └── Sidebar/
├── hooks/            # Hooks customizados
├── assets/           # Imagens e logos
├── types/            # Tipagens TypeScript
├── main.tsx          # Ponto de entrada
└── index.css          # CSS global

````

### Requisitos
- Node.js 18+
- npm ou yarn

### Instalação
```bash
git clone https://github.com/Zer0G0ld/MachineMonitorZ.git
cd MachineMonitorZ
npm install
````

### Execução em desenvolvimento

```bash
npm run dev
```

O frontend estará disponível em `http://localhost:5173`.

### Build para produção

```bash
npm run build
npm run preview
```

### Configuração

* API endpoint do agente é configurado no hook `useMetrics.ts`.

