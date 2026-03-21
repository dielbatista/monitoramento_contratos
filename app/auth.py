import os

def verificar_login(usuario, senha):
    ADMIN_USER = os.getenv("APP_USER", "admin")
    ADMIN_PASS = os.getenv("APP_PASS", "1234")
    return usuario == ADMIN_USER and senha == ADMIN_PASS

def logout(page):
    page.clean()
    page.floating_action_button = None
    # Reset da AppBar para o login não herdar a do dashboard
    page.appbar = None 
    import main 
    main.mostrar_tela_login(page)