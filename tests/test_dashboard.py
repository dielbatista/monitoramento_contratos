import sys
import os
import pytest
from unittest.mock import MagicMock

# --- MOCKS DE SISTEMA ---
if 'psycopg2' not in sys.modules:
    sys.modules['psycopg2'] = MagicMock()
    sys.modules['psycopg2.extras'] = MagicMock()

# Mock do módulo de relatórios para evitar erros de importação de PDF
sys.modules['app.reports'] = MagicMock()

from app import database as db
from app.dashboard import carregar_dashboard
import flet as ft

# --- MOCK DA PÁGINA ---
class MockPage:
    def __init__(self):
        self.views = []
        self.overlay = []
        self.session = MagicMock()
        self.snack_bar = None
        self.route = "/dashboard"
        self.theme_mode = None
        self.title = ""
        self.window_width = 0
        self.window_height = 0
        self.padding = 0
        self.spacing = 0
    
    def update(self):
        pass

    def go(self, route):
        self.route = route

    def launch_url(self, url):
        self.url_lancada = url

@pytest.fixture
def page(monkeypatch):
    # Força ambiente de teste
    monkeypatch.setenv("DB_TYPE", "sqlite")
    
    p = MockPage()
    # Mock padrão de sessão
    p.session.get.return_value = "Diel"
    return p

# --- TESTES ---

def test_carregamento_dashboard_basico(page, monkeypatch):
    """Verifica se o dashboard renderiza a view e busca contratos."""
    # Mock do banco para retornar uma lista vazia e não quebrar o loop
    monkeypatch.setattr(db, "listar_contratos", lambda: [])
    monkeypatch.setattr(db, "verificar_se_admin", lambda u: True)

    carregar_dashboard(page)
    
    # Verifica se a View do dashboard foi adicionada
    assert len(page.views) > 0
    assert page.views[-1].route == "/dashboard"

def test_calculo_status_vencimento(page, monkeypatch):
    """Testa a lógica interna de cores de vencimento (indireto via renderização)"""
    from datetime import date, timedelta
    
    # Cria uma data para daqui a 10 dias (deve ser RED - Vence em breve)
    data_vencimento = (date.today() + timedelta(days=10)).strftime("%d-%m-%Y")
    
    # Mock de um contrato específico
    contrato_fake = [(1, "EMPRESA TESTE", "001", data_vencimento, 1000.0, 0, "01-01-2024")]
    monkeypatch.setattr(db, "listar_contratos", lambda: contrato_fake)
    monkeypatch.setattr(db, "obter_gastos", lambda id: {})
    
    carregar_dashboard(page)
    
    # A lista_view deve ter 1 controle (o container do contrato)
    # O primeiro controle do View é o AppBar, o segundo é a lista_view
    lista_view = page.views[-1].controls[1]
    card_contrato = lista_view.controls[0]
    
    # Verifica se a borda esquerda é vermelha (red) conforme lógica de < 30 dias
    assert card_contrato.border.left.color == "red"

def test_logout_limpa_sessao(page, monkeypatch):
    """Verifica se a função de logout limpa os dados e redireciona"""
    monkeypatch.setattr(db, "listar_contratos", lambda: [])
    carregar_dashboard(page)
    
    # Captura a função de logout do AppBar
    app_bar = page.views[-1].controls[0]
    # O botão de logout é o último controle da actions_row (que é o último da AppBar)
    btn_logout = app_bar.actions[0].controls[-1]
    
    # Executa o clique de logout
    btn_logout.on_click(None)
    
    # Verifica se limpou a sessão e mudou a rota
    page.session.clear.assert_called()
    assert page.route == "/"

def test_restricao_admin_settings(page, monkeypatch):
    """Verifica se o ícone de configurações só aparece para Admins"""
    # 1. Caso NÃO ADMIN
    monkeypatch.setattr(db, "verificar_se_admin", lambda u: False)
    monkeypatch.setattr(db, "listar_contratos", lambda: [])
    
    carregar_dashboard(page)
    actions_row = page.views[-1].controls[0].actions[0]
    
    # Procura o ícone SETTINGS nos controles
    icones = [c.icon for c in actions_row.controls if hasattr(c, 'icon')]
    assert ft.Icons.SETTINGS not in icones

    # 2. Caso ADMIN
    page.views.clear()
    monkeypatch.setattr(db, "verificar_se_admin", lambda u: True)
    
    carregar_dashboard(page)
    actions_row = page.views[-1].controls[0].actions[0]
    icones_admin = [c.icon for c in actions_row.controls if hasattr(c, 'icon')]
    assert ft.Icons.SETTINGS in icones_admin