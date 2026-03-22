# 1. Imagem base estável
FROM python:3.10-slim

# 2. Configurações de ambiente para Python
# PYTHONDONTWRITEBYTECODE: Evita que o Python escreva arquivos .pyc no container
# PYTHONUNBUFFERED: Garante que os logs (prints) apareçam em tempo real no Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Definir diretório de trabalho
WORKDIR /app

# 4. Instalar dependências de sistema (CRÍTICO para Postgres e Bcrypt)
# Instalar apenas o essencial para o Banco de Dados e compilação do Bcrypt
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
# 5. Instalar dependências do Python
# Copiamos apenas o requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copiar o código do projeto
COPY . .

# 7. Expor a porta (deve ser a mesma do seu main.py)
EXPOSE 8080

# 8. Comando para iniciar
CMD ["python", "main.py"]