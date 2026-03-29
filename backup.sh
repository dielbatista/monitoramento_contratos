#!/bin/bash

# --- CONFIGURAÇÕES ---
# Nome do serviço do banco no docker-compose.yml
DB_SERVICE_NAME="db"
# Nome do banco de dados e usuário (conforme seu .env)
DB_NAME="monitoramento_db"
DB_USER="user_admin"
# Pasta onde os backups serão salvos
BACKUP_DIR="./backups"
# Nome do arquivo com data e hora
DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILE_NAME="backup_${DB_NAME}_${DATE}.sql"

# Criar a pasta de backup se não existir
mkdir -p $BACKUP_DIR

# --- EXECUÇÃO ---
echo "Iniciando backup do banco de dados..."

# O comando executa o pg_dump dentro do container e salva o resultado fora
docker-compose exec -T $DB_SERVICE_NAME pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/$FILE_NAME

# Opcional: Remover backups com mais de 7 dias para não encher o disco
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete

echo "Backup concluído com sucesso: $BACKUP_DIR/$FILE_NAME"