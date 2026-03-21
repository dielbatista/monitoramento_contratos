import flet as ft

def carregar_login(page: ft.Page):
    page.views.clear()

    txt_user = ft.TextField(
        label="Usuário", 
        border_radius=10, 
        width=300,
        prefix_icon=ft.icons.PERSON
    )
    txt_pass = ft.TextField(
        label="Senha", 
        password=True, 
        can_reveal_password=True, 
        border_radius=10, 
        width=300,
        prefix_icon=ft.icons.LOCK
    )

    def entrar_clique(e):
    # Verifique se os valores batem exatamente com o que você digita
        if txt_user.value == "admin" and txt_pass.value == "123": 
            print("Login aceito, redirecionando...")
            page.go("/dashboard")
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuário ou senha incorretos!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

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
                            
                            # CORREÇÃO AQUI: Trocamos VerticalDivider por um Container vazio para dar o espaçamento
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