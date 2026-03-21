Sistema de Monitoramento de Contratos 📊
Este é um sistema de gestão financeira focado no controle de saldo e vigência de contratos. O software permite o acompanhamento detalhado de débitos mensais, abatendo automaticamente valores de exercícios anteriores e gastos correntes para fornecer o saldo real disponível em tempo real.

🚀 Funcionalidades
Gestão de Saldos: Cálculo automático baseado na fórmula:
Saldo Atual = Valor Total - Gasto Ano Anterior - Soma de Gastos Mensais.

Controle de Vigência: Alertas visuais de status (Vence em breve, Prazo OK) baseados na data atual.

Lançamentos Mensais: Detalhamento de gastos de Janeiro a Dezembro para cada contrato.

Persistência de Dados: Armazenamento robusto utilizando SQLite.

Interface Moderna: UI responsiva construída com o framework Flet (baseado em Flutter).

Relatórios: Geração de relatórios detalhados em PDF (em implementação).

🛠️ Tecnologias Utilizadas
Linguagem: Python 3.x

Interface Gráfica: Flet

Banco de Dados: SQLite com integração via Python sqlite3

Segurança: Sistema de login com autenticação de usuário.

Versionamento: Git & GitHub com autenticação via SSH.

📋 Pré-requisitos
Antes de começar, você vai precisar ter instalado em sua máquina (ou WSL/Linux):

Python 3.8+

Git

🔧 Instalação e Execução
Siga os passos abaixo no seu terminal:

Clone o repositório:

Bash
git clone git@github.com:dielbatista/monitoramento_contratos.git
cd monitoramento_contratos
Crie um ambiente virtual (Recomendado):

Bash
python3 -m venv .venv
source .venv/bin/activate
Instale as dependências:

Bash
pip install -r requirements.txt
Caso não tenha o arquivo, instale manualmente:
pip install flet fpdf2

Inicie a aplicação:

Bash
python3 main.py
🔐 Acesso ao Sistema
Usuário padrão: admin

Senha padrão: 123

👨‍💻 Autor
Diel Batista Estudante de Engenharia de Software | Full Stack Developer in progress (Focus: Backend)
