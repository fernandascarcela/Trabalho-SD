Estrutura do projeto 

/
├── docker-compose.yml
├── README.md
│
├── clientes/
│   ├── cliente_paciente.py
│   ├── cliente_recepcionista.py
│   ├── cliente_medico.py
│   └── cliente_admin.py
│
├── interfaces/                  # APIs REST para comunicação com os clientes
│   ├── interface_usuarios/
│   │   ├── app.py               # Flask/FastAPI
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── interface_agendamento/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── interface_validacao/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── interface_notificacoes/
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── servicos/                    # Serviços internos (cada um com seu mecanismo exigido)
│   ├── servico_usuarios/        # EX: RPC/RMI
│   │   ├── server/              # lógica interna
│   │   ├── client/              # código chamado pela interface
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── servico_agendamento/     # EX: Sockets TCP
│   │   ├── server/
│   │   ├── client/
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── servico_validacao/       # (em outra linguagem)
│   │   ├── proto/
│   │   │   └── validacao.proto
│   │   ├── python_client/
│   │   ├── go_server/           # ou Java, C#, etc
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   └── servico_notificacoes/    # Publica no RabbitMQ
│       ├── publisher.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── database/
│   ├── init.sql                 # schema inicial
│   ├── Dockerfile
│   └── data/                    # volume persistente
│
├── rabbitmq/
│   └── definitions.json         # filas e exchanges (opcional)
│
└── scripts/
    ├── build.sh
    ├── start.sh
    └── test_endpoints.py
# Trabalho-Final-de-SD
