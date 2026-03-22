import sys
from unittest.mock import MagicMock
import os
import sqlite3

# --- MOCK DO PSYCOPG2 (Necessário para sua estrutura atual) ---
if 'psycopg2' not in sys.modules:
    sys.modules['psycopg2'] = MagicMock()
    sys.modules['psycopg2.extras'] = MagicMock()

import pytest
from app import database as db

TEST_DB = "test_data.db"

@pytest.fixture(autouse=True)
def setup_db():
    """Configura o banco de teste antes de cada execução."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Mock da conexão para garantir que o database.py use o banco de teste
    def mock_conectar():
        conn = sqlite3.connect(TEST_DB)
        conn.row_factory = sqlite3.Row
        return conn
    
    db.conectar = mock_conectar
    db.inicializar_db()
    
    yield
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_case_sensitive_login():
    """Valida se 'Diel' é diferente de 'diel' (COLLATE BINARY)."""
    db.criar_usuario("DielBatista", "senha123", is_admin=True)
    
    # Login exato -> OK
    assert db.verificar_login("DielBatista", "senha123")["valido"] is True
    
    # Login minúsculo -> FALHA
    assert db.verificar_login("dielbatista", "senha123")["valido"] is False

def test_seguranca_senha_hash():
    """Garante que a senha não é texto limpo no banco."""
    senha_real = "123456"
    db.criar_usuario("UsuarioTeste", senha_real, is_admin=False)
    
    conn = sqlite3.connect(TEST_DB)
    res = conn.execute("SELECT senha FROM usuarios WHERE usuario='UsuarioTeste'").fetchone()
    conn.close()
    
    senha_salva = res[0]
    assert senha_salva != senha_real
    assert senha_salva.startswith("$2b$") # Formato do Bcrypt

def test_empresa_sempre_maiuscula():
    """Valida se a regra de negócio de converter empresa para UPPER funciona."""
    db.adicionar_contrato(
        empresa="flet app", 
        n_contrato="999", 
        data_fim="2026-12-31", 
        valor_total=100.0, 
        valor_gasto_anterior=0, 
        data_inicio="2026-01-01"
    )
    
    contratos = db.listar_contratos()
    # Verifica se salvou como "FLET APP"
    assert contratos[0][1] == "FLET APP"