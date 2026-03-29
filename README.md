📑 Sistema de Monitoramento de Contratos
Sistema desenvolvido para gestão e acompanhamento financeiro de contratos, com dashboards interativos, controle de aditivos, saldo global e geração de relatórios detalhados em PDF.

🚀 Tecnologias Utilizadas
Linguagem: Python 3.10+

Interface Gráfica: Flet (Flutter for Python)

Banco de Dados: PostgreSQL (via SQLAlchemy/Psycopg2)

Relatórios: ReportLab (Geração de PDF customizado)

Segurança: Bcrypt (Hashing de senhas)

Testes: Pytest (Suíte completa de testes unitários e mocks)

Containerização: Docker & Docker Compose

🛠️ Funcionalidades
Dashboard Financeiro: Visualização em tempo real de gastos, aditivos e saldo disponível.

Gestão de Contratos: CRUD completo de contratos com monitoramento de vigência.

Relatórios Automáticos: Geração de PDF com resumo financeiro e detalhamento mensal.

Segurança: Sistema de login com níveis de acesso (Admin/User).

Sanitização: Tratamento automático de nomes de arquivos e dados de entrada.

🧪 Qualidade de Código
O projeto conta com uma suíte de testes automatizados cobrindo as principais regras de negócio e utilitários de sistema.

Bash
# Para rodar os testes
pytest -v
Status atual: 20 testes passados (100% de sucesso) incluindo mocks complexos de PDF e interface.

📦 Como rodar com Docker
O projeto está pronto para deploy em containers.

Configure as variáveis de ambiente:
Crie um arquivo .env na raiz com:

Snippet de código
DB_URL=postgresql://usuario:senha@db:5432/nome_do_banco
SECRET_KEY=sua_chave_secreta
Suba o ambiente:

Bash
docker-compose up --build
A aplicação estará disponível em http://localhost:8080.

📂 Estrutura do Projeto
Plaintext
├── app/                # Código fonte principal
│   ├── database.py     # Conexão e modelos do banco
│   ├── reports.py      # Lógica de geração de PDFs
│   ├── dashboard.py    # Interface do Dashboard (Flet)
│   └── main.py         # Ponto de entrada da aplicação
├── tests/              # Testes unitários (Pytest)
├── Dockerfile          # Configuração do container de produção
├── requirements.txt    # Dependências do projeto
└── README.md           # Documentação