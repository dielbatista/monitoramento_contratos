import flet as ft
from app import database as db
from app.login import carregar_login
from app.dashboard import carregar_dashboard

def main(page: ft.Page):
    page.title = "Monitoramento de Contratos"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Configurações de Janela
    page.window.width = 1200
    page.window.height = 800

    # Inicializa o Banco de Dados
    db.init_db()

    # Gerenciador de Rotas
    def route_change(route):
        if page.route == "/":
            carregar_login(page)
        elif page.route == "/dashboard":
            carregar_dashboard(page)
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Inicia a aplicação
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)