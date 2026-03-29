import flet as ft
from app import database as db

def carregar_login(page: ft.Page):
    # Sempre que carregar a tela de login, garantimos que a sessão está limpa
    # Isso resolve o problema de tentar deslogar e o Flet te manter logado
    page.session.clear()
    page.views.clear()

    # --- CAMPOS DE ENTRADA ---
    txt_user = ft.TextField(
        label="Usuário", 
        border_radius=10, 
        width=300,
        prefix_icon=ft.Icons.PERSON,
        on_submit=lambda _: entrar_clique(None)
    )
    
    txt_pass = ft.TextField(
        label="Senha", 
        password=True, 
        can_reveal_password=True, 
        border_radius=10, 
        width=300,
        prefix_icon=ft.Icons.LOCK,
        on_submit=lambda _: entrar_clique(None)
    )

    # --- LÓGICA DE AUTENTICAÇÃO ---
    def entrar_clique(e):
        user = txt_user.value.strip() 
        senha = txt_pass.value.strip()

        if not user or not senha:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        resultado = db.verificar_login(user, senha)

        if resultado["valido"]:
            # Define a sessão
            page.session.set("user_name", user)
            page.session.set("is_admin", resultado["is_admin"])
            
            print(f"Login aceito para {user}, redirecionando...")
            page.go("/dashboard")
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Usuário ou senha incorretos!"), 
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()

    # --- INTERFACE VISUAL ---
    page.views.append(
        ft.View(
            "/",
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.LOCK_PERSON, size=80, color="blue"),
                            ft.Text("SISTEMA DE CONTRATOS", size=24, weight="bold"),
                            ft.Text("Faça login para continuar", color="grey"),
                            ft.Container(height=20), 
                            txt_user,
                            txt_pass,
                            ft.ElevatedButton(
                                "ENTRAR", 
                                on_click=entrar_clique, 
                                bgcolor="blue", 
                                color="white", 
                                width=300, 
                                height=50
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    expand=True,
                    alignment=ft.alignment.center,
                )
            ],
            bgcolor="#F0F2F5"
        )
    )
    page.update()