import flet as ft
from app import database as db
from app.login import carregar_login
from app.dashboard import carregar_dashboard

def main(page: ft.Page):
    # 1. INICIALIZAÇÃO DO BANCO (Cria tabelas e o Admin p3dr0d4v1)
    db.inicializar_db() 

    # 2. CONFIGURAÇÕES DA PÁGINA
    page.title = "Sistema de Gestão de Contratos - NoPaper"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    
    # 3. GERENCIADOR DE ROTAS
    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            carregar_login(page)
            
        elif page.route == "/dashboard":
            # SEGURANÇA: Só permite acesso se houver usuário na sessão
            if not page.session.get("user_name"):
                page.go("/")
                return
            carregar_dashboard(page)
            
        page.update()

    page.on_route_change = route_change
    
    # Garante que inicie na rota correta
    if page.route == "/":
        page.go("/")
    else:
        page.go(page.route)

if __name__ == "__main__":
    # Mantendo a porta 8080 conforme sua preferência e configuração Docker
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=8080,       
        host="0.0.0.0"   
    )