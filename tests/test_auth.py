import sys
from unittest.mock import MagicMock

# --- MOCK DO PSYCOPG2 (Deve vir antes de tudo) ---
if 'psycopg2' not in sys.modules:
    sys.modules['psycopg2'] = MagicMock()
    sys.modules['psycopg2.extras'] = MagicMock()

import pytest
import os
from app import auth

# --- MOCK DA PÁGINA FLET ---
class MockPage:
    def __init__(self):
        self.floating_action_button = "Botão Antigo"
        self.appbar = "AppBar Antiga"
        self.route = "/dashboard"
    
    def clean(self):
        """Simula a limpeza da página."""
        pass

@pytest.fixture
def mock_env(monkeypatch):
    """Define variáveis de ambiente fixas para o teste."""
    monkeypatch.setenv("APP_USER", "admin_teste")
    monkeypatch.setenv("APP_PASS", "senha_teste")

def test_verificar_login_sucesso(mock_env):
    """Valida login com as credenciais do ambiente."""
    resultado = auth.verificar_login("admin_teste", "senha_teste")
    assert resultado is True

def test_verificar_login_falha(mock_env):
    """Garante que credenciais erradas sejam rejeitadas."""
    assert auth.verificar_login("errado", "senha_teste") is False
    assert auth.verificar_login("admin_teste", "123") is False

def test_verificar_login_case_sensitive(mock_env):
    """Valida se o login diferencia maiúsculas (Case-Sensitive)."""
    assert auth.verificar_login("ADMIN_TESTE", "senha_teste") is False

def test_logout_reseta_interface(monkeypatch):
    """Valida se o logout limpa os elementos da tela."""
    page = MockPage()
    
    # Mock do main.mostrar_tela_login
    # Como o logout importa 'main' localmente, mockamos o módulo inteiro
    mock_main = MagicMock()
    monkeypatch.setitem(sys.modules, "main", mock_main)
    
    auth.logout(page)
    
    # Verifica se os elementos foram resetados
    assert page.floating_action_button is None
    assert page.appbar is None
    # Verifica se a função de redirecionamento foi chamada
    mock_main.mostrar_tela_login.assert_called_once_with(page)