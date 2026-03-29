import sys
import os
from unittest.mock import MagicMock

# --- MOCK DO PSYCOPG2 E DATABASE ---
# Evita erros de importação e conexão com banco real durante o teste de interface
if 'psycopg2' not in sys.modules:
    sys.modules['psycopg2'] = MagicMock()
    sys.modules['psycopg2.extras'] = MagicMock()

import pytest
import flet as ft
from main import main as main_app

# --- MOCK DA SESSÃO ---
class MockSession:
    def __init__(self):
        self.data = {}
    def set(self, key, value):
        self.data[key] = value
    def get(self, key):
        return self.data.get(key)
    def clear(self):
        self.data.clear()

# --- MOCK DA PÁGINA (VERSÃO COMPLETA) ---
class MockPage:
    def __init__(self):
        self.views = []
        self.overlay = []
        self.route = "/"
        self.session = MockSession()
        self.title = ""
        self.window_width = 0
        self.window_height = 0
        self.theme_mode = None
        self.snack_bar = None
        self.padding = 0
        self.spacing = 0
        self.on_route_change = None
        self.on_view_pop = None
    
    def update(self):
        pass

    def add(self, *args):
        pass
    
    def go(self, route):
        self.route = route
        if self.on_route_change:
            class Event: pass
            e = Event()
            e.route = route
            self.on_route_change(e)

@pytest.fixture
def page(monkeypatch):
    # Força o DB_TYPE para sqlite para o inicializar_db() do main não quebrar
    monkeypatch.setenv("DB_TYPE", "sqlite")
    return MockPage()

# --- TESTES ---

def test_configuracoes_iniciais(page):
    """Verifica se o título e dimensões batem com o main.py"""
    main_app(page)
    # Ajustado para o título real que está no seu main.py
    assert page.title == "Sistema de Monitoramento de Contratos"
    assert page.window_width == 1200
    assert page.theme_mode == ft.ThemeMode.LIGHT

def test_bloqueio_dashboard_sem_login(page):
    """Garante que sem usuário na sessão, o sistema redireciona para a raiz"""
    main_app(page)
    # Tenta ir para o dashboard sem setar usuário
    page.go("/dashboard")
    # A lógica do main.py deve jogar de volta para "/"
    assert page.route == "/"

def test_acesso_dashboard_com_login(page):
    """Verifica se com login o acesso ao dashboard é permitido"""
    main_app(page)
    # Simula usuário logado
    page.session.set("user_name", "Diel Batista")
    
    page.go("/dashboard")
    assert page.route == "/dashboard"

def test_logica_logout(page):
    """Verifica se a rota de logout limpa a sessão e redireciona"""
    main_app(page)
    page.session.set("user_name", "Diel")
    
    # Aciona a rota de logout definida no seu main.py
    page.go("/logout")
    
    assert page.session.get("user_name") is None
    assert page.route == "/"

def test_redirecionamento_login_ja_logado(page):
    """Se o usuário já está logado e tenta ir para a raiz, deve ir para o dashboard"""
    page.session.set("user_name", "Diel")
    main_app(page)
    
    # Tenta ir para a raiz "/"
    page.go("/")
    
    # O main.py redireciona para o dashboard automaticamente
    assert page.route == "/dashboard"