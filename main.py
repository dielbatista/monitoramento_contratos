import flet as ft
from app import database as db
from app.login import carregar_login
from app.dashboard import carregar_dashboard

def main(page: ft.Page):
    # 1. INICIALIZAÇÃO DO BANCO
    try:
        db.inicializar_db() 
    except Exception as e:
        print(f"ERRO CRÍTICO NO BANCO: {e}")
        page.add(ft.Text(f"Erro ao conectar ao banco: {e}", color="red"))
        return

    # 2. CONFIGURAÇÕES DA PÁGINA
    page.title = "Sistema de Monitoramento de Contratos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.window_width = 1200
    page.window_height = 800

    # 3. GERENCIADOR DE ROTAS (Lógica de Proteção)
    def route_change(e):
        # Limpa as views para evitar sobreposição
        page.views.clear()
        
        # Recupera o usuário da sessão
        user = page.session.get("user_name")
        
        # --- Lógica de Roteamento ---

        # NOVA ROTA DE LOGOUT: Limpa tudo e vai para a raiz
        if page.route == "/logout":
            page.session.clear()
            page.views.clear()
            page.go("/")
            return

        # Se tentar acessar o Dashboard
        if page.route == "/dashboard":
            if not user:
                # Se não houver login, redireciona para a raiz
                page.go("/")
                return 
            else:
                carregar_dashboard(page)
        
        # Rota de Login (Raiz)
        elif page.route == "/" or page.route == "" or page.route is None:
            if user:
                # Se já estiver logado, manda pro dashboard
                page.go("/dashboard")
                return
            carregar_login(page)
            
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # 4. DISPARO INICIAL
    page.go(page.route)

if __name__ == "__main__":
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=8080,      
        host="0.0.0.0"   
    )