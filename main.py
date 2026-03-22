import flet as ft
from app import database as db
from app.login import carregar_login
from app.dashboard import carregar_dashboard
import time

def main(page: ft.Page):
    # 1. INICIALIZAÇÃO DO BANCO (Com tratamento de erro para Docker)
    try:
        print("Tentando conectar ao banco de dados...")
        db.inicializar_db() 
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"ERRO CRÍTICO NA INICIALIZAÇÃO DO BANCO: {e}")
        # Em ambiente Docker, se o banco falhar, mostramos o erro no log e paramos
        return

    # 2. CONFIGURAÇÕES DA PÁGINA
    page.title = "Sistema de Gestão de Contratos - NoPaper"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Responsividade básica para o navegador
    page.window.width = 1200
    page.window.height = 800
    
    # 3. GERENCIADOR DE ROTAS
    def route_change(e):
        # Limpa as views atuais para evitar sobreposição visual
        page.views.clear()
        
        if page.route == "/":
            carregar_login(page)
            
        elif page.route == "/dashboard":
            # SEGURANÇA: Verifica se o usuário está logado na sessão
            if not page.session.get("user_name"):
                print("Acesso negado: Usuário não logado. Redirecionando...")
                page.go("/")
            else:
                carregar_dashboard(page)
        
        page.update()

    page.on_route_change = route_change
    
    # 4. INICIALIZAÇÃO DE ROTA
    # Garante que sempre comece no login se não houver rota definida
    if page.route == "/":
        page.go("/")
    else:
        # Se for um refresh no /dashboard, o route_change valida a sessão
        page.go(page.route)

if __name__ == "__main__":
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=8501,       
        host="0.0.0.0"   
    )