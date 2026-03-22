import sys
from unittest.mock import MagicMock

# --- MOCK DO PSYCOPG2 ---
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

# --- MOCK DA PÁGINA (VERSÃO COMPLETA) ---
class MockPage:
    def __init__(self):
        self.views = []
        self.overlay = [] # Adicionado para resolver o erro do dashboard
        self.route = "/"
        self.session = MockSession()
        self.title = ""
        self.window_width = 0
        self.window_height = 0
        self.theme_mode = None
        self.snack_bar = None
    
    def update(self):
        pass
    
    def go(self, route):
        self.route = route
        if hasattr(self, 'on_route_change'):
            class Event: pass
            e = Event()
            e.route = route
            self.on_route_change(e)

@pytest.fixture
def page():
    return MockPage()

def test_configuracoes_iniciais(page):
    main_app(page)
    assert page.title == "Sistema de Gestão de Contratos - NoPaper"
    assert page.window_width == 1200

def test_bloqueio_dashboard_sem_login(page):
    main_app(page)
    page.go("/dashboard")
    assert page.route == "/"

def test_acesso_dashboard_com_login(page):
    main_app(page)
    # Simula login
    page.session.set("user_name", "Diel")
    
    # Agora com 'overlay' presente, o dashboard não vai quebrar
    page.go("/dashboard")
    
    assert page.route == "/dashboard"