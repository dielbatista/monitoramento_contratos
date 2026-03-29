import sys
import os
import sqlite3
import pytest
from unittest.mock import MagicMock

# --- MOCK DO PSYCOPG2 ---
# Evita que o pytest tente carregar o driver de Postgres real
if 'psycopg2' not in sys.modules:
    sys.modules['psycopg2'] = MagicMock()
    sys.modules['psycopg2.extras'] = MagicMock()

from app import database as db

TEST_DB = "test_contratos.db"

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    """Configura o ambiente de teste isolado usando SQLite."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Força o uso do SQLite para os testes
    monkeypatch.setenv("DB_TYPE", "sqlite")
    
    # Mock da conexão para o banco de teste
    def mock_conectar():
        conn = sqlite3.connect(TEST_DB)
        conn.row_factory = sqlite3.Row
        return conn
    
    monkeypatch.setattr(db, "conectar", mock_conectar)
    db.inicializar_db()
    
    yield
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

# --- TESTES DE SEGURANÇA ---

def test_login_case_sensitive():
    """Valida se o login diferencia maiúsculas de minúsculas."""
    db.criar_usuario("DielBatista", "senha123", is_admin=True)
    assert db.verificar_login("DielBatista", "senha123")["valido"] is True
    assert db.verificar_login("dielbatista", "senha123")["valido"] is False

def test_seguranca_senha_hash():
    """Garante que a senha é salva com hash Bcrypt."""
    senha_limpa = "admin123"
    db.criar_usuario("SegurancaTeste", senha_limpa, is_admin=False)
    
    conn = sqlite3.connect(TEST_DB)
    res = conn.execute("SELECT senha FROM usuarios WHERE usuario='SegurancaTeste'").fetchone()
    conn.close()
    
    assert res[0] != senha_limpa
    assert res[0].startswith("$2b$")

# --- TESTES DE CONTRATOS ---

def test_empresa_sempre_maiuscula():
    """Valida a normalização do nome da empresa para CAIXA ALTA."""
    db.adicionar_contrato(
        empresa="empresa teste", 
        n_contrato="123", 
        data_fim="31-12-2026", 
        valor_total=1000.0, 
        valor_gasto_anterior=0, 
        data_inicio="01-01-2026"
    )
    
    contratos = db.listar_contratos()
    assert contratos[0][1] == "EMPRESA TESTE"

# --- TESTE DE ADITIVO (AJUSTADO PARA A ORDEM DA SUA FUNÇÃO) ---

def test_atualizar_contrato_aditivo():
    """Valida se a atualização de aditivo reflete no contrato e gera histórico."""
    # 1. Cria contrato inicial (Total 1000.0)
    db.adicionar_contrato("LOJA", "001", "01-01-2025", 1000.0, 0, "01-01-2024")
    c_id = db.listar_contratos()[0][0]

    # 2. Define os valores conforme a assinatura da sua função:
    # (c_id, novo_total, nova_data, valor_somado)
    valor_do_aditivo = 500.0
    novo_total_calculado = 1500.0
    nova_data_fim = "01-01-2027"

    # CHAMADA CORRIGIDA: Seguindo a ordem exata do seu database.py
    db.atualizar_contrato_aditivo(c_id, novo_total_calculado, nova_data_fim, valor_do_aditivo)

    # 3. Verifica se o contrato principal foi atualizado
    contratos = db.listar_contratos()
    assert contratos[0][4] == 1500.0  # valor_total atualizado
    assert contratos[0][3] == "01-01-2027"  # data_fim atualizada

    # 4. Verifica se o registro no histórico de aditivos foi criado
    aditivos = db.listar_aditivos(c_id)
    assert len(aditivos) == 1
    assert float(aditivos[0][5]) == 500.0  # valor_aditivo na tabela aditivos
    assert aditivos[0][2] == "1"            # numero_aditivo (proximo_numero)