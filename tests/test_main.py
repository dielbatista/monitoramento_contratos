import pytest
import sqlite3
import os
from main import init_db, importar_dados

# Configurações para o teste
TEST_DB = "test_contratos.db"
TEST_CSV = "dados.csv" # Usaremos o seu csv real para validar a estrutura

def test_banco_criado_com_sucesso():
    """Verifica se as tabelas e o usuário do ENV são criados."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    init_db(db_path=TEST_DB)
    
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    
    # Verifica tabela contratos
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contratos'")
    assert cursor.fetchone() is not None
    
    # Verifica se o usuário padrão foi inserido
    cursor.execute("SELECT user FROM usuarios")
    user = cursor.fetchone()
    assert user[0] == os.getenv("APP_USER", "admin")
    
    conn.close()

def test_importacao_csv_para_sql():
    """Verifica se os dados do CSV estão chegando corretamente no SQL."""
    # Garante banco limpo
    init_db(db_path=TEST_DB)
    
    sucesso, mensagem = importar_dados(csv_path=TEST_CSV, db_path=TEST_DB)
    
    assert sucesso is True
    
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contratos")
    quantidade = cursor.fetchone()[0]
    
    # Verifica se importou ao menos uma linha (ajuste conforme seu CSV)
    assert quantidade > 0
    
    # Verifica se o saldo é um número (float)
    cursor.execute("SELECT saldo FROM contratos LIMIT 1")
    saldo = cursor.fetchone()[0]
    assert isinstance(saldo, float)
    
    conn.close()

# Cleanup: remove o banco de teste após rodar
def teardown_module(module):
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)