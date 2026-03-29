import flet as ft
from app import database as db
from datetime import datetime, date
import base64

def carregar_dashboard(page: ft.Page):
    # --- RECUPERAÇÃO DE SESSÃO E PERMISSÕES ---
    user_name = page.session.get("user_name") or "Usuário"
    is_admin = db.verificar_se_admin(user_name)

    # --- FUNÇÃO DE LOGOUT ---
    def acao_logout(e):
        page.session.clear()
        page.views.clear()
        page.go("/")

    # --- UTILITÁRIOS ---
    def formatar_moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def converter_para_float(valor_str):
        """Converte string de moeda ou formatada para float puro."""
        if not valor_str: return 0.0
        try:
            limpo = str(valor_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(limpo)
        except ValueError:
            return 0.0

    def calcular_status_vencimento(data_str):
        if not data_str: return {"cor": "grey", "label": "SEM DATA"}
        hoje = date.today()
        venc = None
        for formato in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                venc = datetime.strptime(data_str.strip(), formato).date()
                break 
            except ValueError: continue
        if venc:
            dias = (venc - hoje).days
            if dias <= 30: return {"cor": "red", "label": "VENCE EM BREVE"}
            elif 30 < dias <= 60: return {"cor": "orange", "label": "ATENÇÃO AO PRAZO"}
            else: return {"cor": "green", "label": "PRAZO OK"}
        return {"cor": "grey", "label": "DATA INVÁLIDA"}

    def calcular_status_saldo(saldo):
        if saldo <= 25000: return {"cor": "red", "label": "SALDO CRÍTICO"}
        return {"cor": "green", "label": "SALDO OK"} if saldo > 50000 else {"cor": "orange", "label": "SALDO BAIXO"}

    # --- CAMPOS E LOGICA PARA ADITIVO ---
    txt_valor_aditivo = ft.TextField(label="Valor Adicional", prefix_text="R$ ", border_radius=10)
    txt_nova_data_aditivo = ft.TextField(label="Novo Vencimento (DD-MM-AAAA)", border_radius=10)

    def aplicar_aditivo(e, contrato_id, valor_atual, data_atual):
        try:
            v_add = converter_para_float(txt_valor_aditivo.value)
            novo_total = valor_atual + v_add
            nova_data = txt_nova_data_aditivo.value if txt_nova_data_aditivo.value else data_atual
            
            db.atualizar_contrato_aditivo(contrato_id, novo_total, nova_data, v_add)\
            
            modal_aditivo.open = False
            modal_detalhes.open = False
            atualizar_lista()

            page.snack_bar = ft.SnackBar(ft.Text(f"Aditivo de {formatar_moeda(v_add)} aplicado!"), bgcolor="green")
            page.snack_bar.open = True
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {err}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    modal_aditivo = ft.AlertDialog(
        title=ft.Text("Aplicar Aditivo"),
        content=ft.Column([
            ft.Text("Informe o valor a ser somado ao total."),
            txt_valor_aditivo,
            txt_nova_data_aditivo
        ], tight=True, spacing=15),
        actions=[
            ft.ElevatedButton("Confirmar Aditivo", bgcolor="orange", color="white", on_click=None),
            ft.TextButton("Cancelar", on_click=lambda _: (setattr(modal_aditivo, "open", False), page.update()))
        ]
    )
    page.overlay.append(modal_aditivo)

    # --- MODAL: GERENCIAR USUÁRIOS ---
    new_user_login = ft.TextField(label="Novo Usuário", border_radius=10)
    new_user_pass = ft.TextField(label="Senha", password=True, can_reveal_password=True, border_radius=10)
    check_is_admin = ft.Checkbox(label="Dar privilégios de Administrador", value=False)

    def salvar_usuario(e):
        if not new_user_login.value or not new_user_pass.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"), bgcolor="red")
        else:
            sucesso = db.criar_usuario(new_user_login.value.strip(), new_user_pass.value, check_is_admin.value)
            if sucesso:
                page.snack_bar = ft.SnackBar(ft.Text(f"Usuário {new_user_login.value} criado!"), bgcolor="green")
                modal_usuarios.open = False
                new_user_login.value = ""; new_user_pass.value = ""; check_is_admin.value = False
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Erro: Usuário já existe."), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    modal_usuarios = ft.AlertDialog(
        title=ft.Row([ft.Icon(ft.Icons.PERSON_ADD, color="blue"), ft.Text("Gerenciar Usuários")]),
        content=ft.Column([ft.Text("Cadastrar Novo Acesso", weight="bold", size=16), new_user_login, new_user_pass, check_is_admin], tight=True, spacing=15),
        actions=[
            ft.ElevatedButton("Criar Usuário", on_click=salvar_usuario, bgcolor="blue", color="white"),
            ft.TextButton("Cancelar", on_click=lambda _: (setattr(modal_usuarios, "open", False), page.update()))
        ]
    )
    page.overlay.append(modal_usuarios)

    # --- MODAL DETALHES ---
    detalhe_empresa = ft.Text("", size=22, weight="bold", color="blue")
    detalhe_corpo = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, height=500)
    modal_detalhes = ft.AlertDialog(title=detalhe_empresa, content=ft.Container(width=750, content=detalhe_corpo))
    page.overlay.append(modal_detalhes)

    def abrir_detalhes(d):
        detalhe_corpo.controls.clear()
        c_id, emp, num, venc, total_inicial, saldo_anterior, dt_inicio = d
        gastos_db = db.obter_gastos(c_id)
        
        txt_saldo_display = ft.Text("", size=16, weight="bold", color="white")
        header_financeiro = ft.Container(padding=20, border_radius=15, bgcolor="F0F2F5", border=ft.border.all(1, ft.colors.BLUE))

        campos_meses = {}
        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        col1, col2 = ft.Column(expand=True, spacing=10), ft.Column(expand=True, spacing=10)

        def atualizar_calculo_dinamico(e=None):
            total_gasto_tela = sum(converter_para_float(campo.value) for campo in campos_meses.values())
            saldo_atual = total_inicial - saldo_anterior - total_gasto_tela
            txt_saldo_display.value = formatar_moeda(saldo_atual)
            txt_saldo_display.color = "white"
            txt_saldo_display.color = "green_accent_400" if saldo_atual > 25000 else "red_accent_100"
            header_financeiro.bgcolor = ft.colors.BLUE if saldo_atual > 25000 else ft.colors.RED_900
            page.update()

        for i, nome in enumerate(meses_nomes, 1):
            v_salvo = gastos_db.get(i, 0.0)
            campo = ft.TextField(
                label=f"Gasto em {nome}", 
                value=f"{v_salvo:.2f}".replace(".", ","), 
                prefix_text="R$ ", 
                border_radius=10, 
                text_size=12,
                on_change=atualizar_calculo_dinamico
            )
            campos_meses[i] = campo
            if i <= 6: col1.controls.append(campo)
            else: col2.controls.append(campo)

        header_financeiro.content = ft.Row([
            ft.Column([ft.Text("VALOR TOTAL", color="white70", size=10), ft.Text(formatar_moeda(total_inicial), color="white", size=16, weight="bold")], expand=True, horizontal_alignment="center"),
            ft.VerticalDivider(color="white24"),
            ft.Column([ft.Text("GASTO ANTERIOR", color="white70", size=10), ft.Text(formatar_moeda(saldo_anterior), color="orange_accent_100", size=16, weight="bold")], expand=True, horizontal_alignment="center"),
            ft.VerticalDivider(color="white24"),
            ft.Column([ft.Text("SALDO ATUAL", color="white70", size=10), txt_saldo_display], expand=True, horizontal_alignment="center"),
        ])

        atualizar_calculo_dinamico()

        def acao_gerar_pdf(e):
            try:
                from app.reports import gerar_pdf_contrato
                page.snack_bar = ft.SnackBar(ft.Text("Gerando relatório PDF..."), duration=2000)
                page.snack_bar.open = True
                page.update()
                
                # Usa os dados atuais do banco para o PDF
                pdf_bytes, _ = gerar_pdf_contrato(d, gastos_db)
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                data_uri = f"data:application/pdf;base64,{pdf_base64}"
                page.launch_url(data_uri)
            except Exception as err:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao gerar PDF: {err}"), bgcolor="red_800")
                page.snack_bar.open = True
            page.update()

        def acao_salvar(e):
            for idx, campo in campos_meses.items():
                db.registrar_gasto(c_id, idx, converter_para_float(campo.value))
            modal_detalhes.open = False
            atualizar_lista()
            page.snack_bar = ft.SnackBar(ft.Text("Lançamentos salvos!"), bgcolor="green")
            page.snack_bar.open = True
            page.update()

        def abrir_modal_aditivo(e):
            txt_valor_aditivo.value = "0"
            txt_nova_data_aditivo.value = venc
            modal_aditivo.actions[0].on_click = lambda _: aplicar_aditivo(_, c_id, total_inicial, venc)
            modal_aditivo.open = True
            page.update()

        detalhe_empresa.value = emp.upper()
        detalhe_corpo.controls = [
            header_financeiro,
            ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH, color="blue", size=20), ft.Text(f"VIGÊNCIA: {dt_inicio} até {venc}", weight="bold")]),
            ft.Row([col1, col2], alignment="start"),
        ]

        # BOTÕES RESTAURADOS AQUI
        modal_detalhes.actions = [
            ft.ElevatedButton("ADITIVO", icon=ft.Icons.POST_ADD, bgcolor=ft.colors.ORANGE_800, color="white", on_click=abrir_modal_aditivo),
            ft.ElevatedButton("GERAR PDF", icon=ft.Icons.PICTURE_AS_PDF, bgcolor=ft.colors.YELLOW_700, color="white", on_click=acao_gerar_pdf),
            ft.ElevatedButton("SALVAR GASTOS", icon=ft.Icons.SAVE, bgcolor="green", color="white", on_click=acao_salvar),
            ft.TextButton("Fechar", on_click=lambda _: (setattr(modal_detalhes, "open", False), page.update()))
        ]
        modal_detalhes.open = True
        page.update()

    # --- FORMULÁRIO DE CADASTRO ---
    txt_empresa = ft.TextField(label="Empresa", border_radius=10)
    txt_num = ft.TextField(label="Nº Contrato", expand=True, border_radius=10)
    txt_data_inicio = ft.TextField(label="Início (DD-MM-AAAA)", expand=True, border_radius=10)
    txt_venc = ft.TextField(label="Vencimento (DD-MM-AAAA)", expand=True, border_radius=10)
    txt_saldo_total = ft.TextField(label="Valor Total", prefix_text="R$ ", expand=True, border_radius=10)
    txt_saldo_anterior = ft.TextField(label="Gasto Anos Ant.", prefix_text="R$ ", expand=True, border_radius=10)
    txt_descricao = ft.TextField(label="Descrição", multiline=True, min_lines=3, max_lines=5, border_radius=10)

    def salvar_novo(e):
        try:
            db.adicionar_contrato(txt_empresa.value.upper(), txt_num.value, txt_venc.value, txt_saldo_total.value, txt_saldo_anterior.value, txt_data_inicio.value)
            modal_add.open = False
            for f in [txt_empresa, txt_num, txt_data_inicio, txt_venc, txt_saldo_total, txt_saldo_anterior, txt_descricao]: f.value = ""
            atualizar_lista()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao cadastrar: {err}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
    
    modal_add = ft.AlertDialog(
        title=ft.Text("Cadastrar Novo Contrato"),
        content=ft.Container(width=500, content=ft.Column([txt_empresa, ft.Row([txt_num, txt_data_inicio]), ft.Row([txt_venc, txt_saldo_total]), txt_saldo_anterior, txt_descricao], tight=True, spacing=15)),
        actions=[ft.ElevatedButton("Cadastrar", on_click=salvar_novo, bgcolor="blue", color="white")]
    )
    page.overlay.append(modal_add)

    lista_view = ft.ListView(expand=True, spacing=10, padding=20)

    def atualizar_lista():
        lista_view.controls.clear()
        dados = db.listar_contratos()
        for d in dados:
            rid, emp, num, ven, total, s_ant, d_ini = d
            g_db = db.obter_gastos(rid)
            saldo_r = total - s_ant - sum(g_db.values())
            st_v, st_s = calcular_status_vencimento(ven), calcular_status_saldo(saldo_r)
            lista_view.controls.append(
                ft.Container(
                    bgcolor="white", padding=15, border_radius=12, on_click=lambda e, dt=d: abrir_detalhes(dt),
                    border=ft.border.only(left=ft.BorderSide(6, st_v["cor"])),
                    content=ft.Row([
                        ft.Icon(ft.Icons.FILE_COPY_ROUNDED, color="blue_grey"),
                        ft.Column([ft.Text(emp.upper(), weight="bold"), ft.Row([ft.Container(ft.Text(st_v["label"], size=9, color="white"), bgcolor=st_v["cor"], padding=5, border_radius=4), ft.Container(ft.Text(st_s["label"], size=9, color="white"), bgcolor=st_s["cor"], padding=5, border_radius=4)])], expand=True),
                        ft.Text(formatar_moeda(saldo_r), weight="bold", color="green" if saldo_r > 25000 else "red"),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red_300", on_click=lambda e, r=rid: (db.deletar_contrato(r), atualizar_lista()))
                    ])
                )
            )
        page.update()
    
    actions_row = ft.Row([
        ft.Icon(ft.Icons.PERSON, color="blue_grey", size=20),
        ft.Text(f"Olá, {user_name.capitalize()}", weight="bold", color="blue_grey"),
        ft.VerticalDivider(width=10, color="transparent"),
    ], spacing=10, vertical_alignment="center")

    if is_admin:
        actions_row.controls.insert(2, ft.IconButton(ft.Icons.SETTINGS, tooltip="Gerenciar Usuários", on_click=lambda _: (setattr(modal_usuarios, "open", True), page.update())))

    actions_row.controls.append(ft.IconButton(ft.Icons.LOGOUT, on_click=acao_logout, icon_color="red_400"))

    page.views.append(
        ft.View("/dashboard", [
            ft.AppBar(title=ft.Text("Monitoramento de Contratos"), center_title=False, bgcolor="white", actions=[actions_row]),
            lista_view,
            ft.FloatingActionButton(content=ft.Icon(ft.Icons.ADD, color="white"), on_click=lambda _: (setattr(modal_add, "open", True), page.update()), bgcolor="blue")
        ], bgcolor="#F0F2F5")
    )
    atualizar_lista()