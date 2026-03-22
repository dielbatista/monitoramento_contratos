import flet as ft
from app import database as db

def carregar_login(page: ft.Page):
    page.views.clear()

    # --- CAMPOS DE ENTRADA ---
    txt_user = ft.TextField(
        label="Usuário", 
        border_radius=10, 
        width=300,
        prefix_icon=ft.icons.PERSON,
        on_submit=lambda _: entrar_clique(None) # Permite logar apertando Enter
    )
    
    txt_pass = ft.TextField(
        label="Senha", 
        password=True, 
        can_reveal_password=True, 
        border_radius=10, 
        width=300,
        prefix_icon=ft.icons.LOCK,
        on_submit=lambda _: entrar_clique(None) # Permite logar apertando Enter
    )

    # --- LÓGICA DE AUTENTICAÇÃO ---
    def entrar_clique(e):
        # Mantém o valor original para o Case-Sensitive no banco de dados
        user = txt_user.value.strip() 
        senha = txt_pass.value.strip()

        if not user or not senha:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        # Consulta o banco de dados (que já está configurado com COLLATE BINARY)
        resultado = db.verificar_login(user, senha)

        if resultado["valido"]:
            # Armazena a sessão com o nome exatamente como digitado
            page.session.set("user_name", user)
            page.session.set("is_admin", resultado["is_admin"])
            
            print(f"Login aceito para {user}, redirecionando...")
            page.go("/dashboard")
        else:
            # Feedback genérico de erro
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
                            ft.Icon(ft.icons.LOCK_PERSON, size=80, color="blue"),
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