import flet as ft
from app import database as db
from datetime import datetime, date

def carregar_dashboard(page: ft.Page):
    # --- FORMATADORES E UTILITÁRIOS ---
    def formatar_moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def limpar_valor_monetario(txt):
        if not txt or str(txt).strip() == "": return "0.0"
        res = txt.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        return res if res else "0.0"

    # FUNÇÃO CORRIGIDA: Tenta ler o formato brasileiro e o do banco
    def calcular_status_vencimento(data_str):
        if not data_str: return {"cor": "grey", "label": "SEM DATA"}
        
        hoje = date.today()
        venc = None
        
        # Tenta converter os formatos possíveis (BR e ISO)
        for formato in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                venc = datetime.strptime(data_str.strip(), formato).date()
                break 
            except ValueError:
                continue

        if venc:
            dias = (venc - hoje).days
            if dias <= 30: return {"cor": "red", "label": "VENCE EM BREVE"}
            elif 30 < dias <= 60: return {"cor": "orange", "label": "ATENÇÃO AO PRAZO"}
            else: return {"cor": "green", "label": "PRAZO OK"}
        
        return {"cor": "grey", "label": "DATA INVÁLIDA"}

    def calcular_status_saldo(saldo):
        if saldo <= 25000: return {"cor": "red", "label": "SALDO CRÍTICO"}
        return {"cor": "green", "label": "SALDO OK"} if saldo > 50000 else {"cor": "orange", "label": "SALDO BAIXO"}

    # --- MODAL DE DETALHES ---
    detalhe_empresa = ft.Text("", size=22, weight="bold", color="blue")
    detalhe_corpo = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, height=500)

    modal_detalhes = ft.AlertDialog(
        title=detalhe_empresa,
        content=ft.Container(width=750, content=detalhe_corpo),
        actions_alignment=ft.MainAxisAlignment.END 
    )
    page.overlay.append(modal_detalhes)

    def abrir_detalhes(d):
        detalhe_corpo.controls.clear()
        # d: (id, empresa, numero, venc, total, saldo_ant, desc, data_inicio)
        c_id, emp, num, venc, total_inicial, saldo_anterior, desc, dt_inicio = d
        
        gastos_db = db.obter_gastos(c_id)
        total_gasto_atual = sum(gastos_db.values())
        
        # REGRA: Saldo = Total - Gasto Ano Anterior - Gastos Mensais
        saldo_restante = total_inicial - saldo_anterior - total_gasto_atual
        
        detalhe_empresa.value = emp.upper()

        header_financeiro = ft.Container(
            bgcolor=ft.colors.BLUE_GREY_900 if saldo_restante > 25000 else ft.colors.RED_900,
            padding=20, border_radius=15,
            content=ft.Row([
                ft.Column([ft.Text("VALOR TOTAL", color="white70", size=10), ft.Text(formatar_moeda(total_inicial), color="white", size=16, weight="bold")], expand=True, horizontal_alignment="center"),
                ft.VerticalDivider(color="white24"),
                ft.Column([ft.Text("GASTO ANTERIOR", color="white70", size=10), ft.Text(formatar_moeda(saldo_anterior), color="orange_accent_100", size=16, weight="bold")], expand=True, horizontal_alignment="center"),
                ft.VerticalDivider(color="white24"),
                ft.Column([ft.Text("SALDO ATUAL", color="white70", size=10), ft.Text(formatar_moeda(saldo_restante), color="green_accent_400" if saldo_restante > 25000 else "red_accent_100", size=16, weight="bold")], expand=True, horizontal_alignment="center"),
            ])
        )

        campos_meses = {}
        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        col1, col2 = ft.Column(expand=True, spacing=10), ft.Column(expand=True, spacing=10)

        for i, nome in enumerate(meses_nomes, 1):
            v_salvo = gastos_db.get(i, 0.0)
            campo = ft.TextField(label=f"Gasto em {nome}", value=f"{v_salvo:.2f}", prefix_text="R$ ", border_radius=10, text_size=12)
            campos_meses[i] = campo
            if i <= 6: col1.controls.append(campo)
            else: col2.controls.append(campo)

        def acao_salvar(e):
            for idx, campo in campos_meses.items():
                db.registrar_gasto(c_id, idx, float(limpar_valor_monetario(campo.value)))
            abrir_detalhes(d)
            atualizar_lista()
            page.snack_bar = ft.SnackBar(ft.Text("Lançamentos salvos!"), bgcolor="green"); page.snack_bar.open = True; page.update()

        detalhe_corpo.controls = [
            header_financeiro,
            ft.Row([
                ft.Icon(ft.icons.CALENDAR_MONTH, color="blue", size=20),
                ft.Text(f"VIGÊNCIA: {dt_inicio} até {venc}", weight="bold")
            ]),
            ft.Row([col1, col2], alignment="start"),
            ft.Divider(),
            ft.Text("Descrição do Contrato:", weight="bold", size=12),
            ft.Container(content=ft.Text(desc if desc else "Sem observações."), bgcolor="#F0F2F5", padding=15, border_radius=10, width=700)
        ]

        modal_detalhes.actions = [
            ft.ElevatedButton("GERAR PDF", icon=ft.icons.PICTURE_AS_PDF, bgcolor="orange", color="white"),
            ft.ElevatedButton("SALVAR GASTOS", icon=ft.icons.SAVE, bgcolor="green", color="white", on_click=acao_salvar),
            ft.TextButton("Fechar", on_click=lambda _: (setattr(modal_detalhes, "open", False), page.update()))
        ]
        modal_detalhes.open = True; page.update()

    # --- FORMULÁRIO ---
    txt_empresa = ft.TextField(label="Empresa", border_radius=10)
    txt_num = ft.TextField(label="Nº Contrato", expand=True, border_radius=10)
    txt_data_inicio = ft.TextField(label="Início (DD-MM-AAAA)", expand=True, border_radius=10)
    txt_venc = ft.TextField(label="Vencimento (DD-MM-AAAA)", expand=True, border_radius=10)
    txt_saldo_total = ft.TextField(label="Valor Total", prefix_text="R$ ", expand=True, border_radius=10)
    txt_saldo_anterior = ft.TextField(label="Gasto Anos Ant.", prefix_text="R$ ", expand=True, border_radius=10)
    txt_desc = ft.TextField(label="Descrição", multiline=True, min_lines=5, max_lines=8, border_radius=10)

    def salvar_novo(e):
        try:
            db.adicionar_contrato(
                txt_empresa.value.upper(), txt_num.value, txt_venc.value,
                float(limpar_valor_monetario(txt_saldo_total.value)),
                float(limpar_valor_monetario(txt_saldo_anterior.value)),
                txt_desc.value, txt_data_inicio.value
            )
            modal_add.open = False
            for f in [txt_empresa, txt_num, txt_data_inicio, txt_venc, txt_saldo_total, txt_saldo_anterior, txt_desc]: f.value = ""
            atualizar_lista()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {err}"), bgcolor="red"); page.snack_bar.open = True; page.update()

    modal_add = ft.AlertDialog(
        title=ft.Text("Cadastrar Novo Contrato"),
        content=ft.Container(width=500, content=ft.Column([
            txt_empresa, ft.Row([txt_num, txt_data_inicio]),
            ft.Row([txt_venc, txt_saldo_total]), txt_saldo_anterior, txt_desc
        ], tight=True, spacing=15)),
        actions=[ft.ElevatedButton("Cadastrar", on_click=salvar_novo, bgcolor="blue", color="white")]
    )
    page.overlay.append(modal_add)

    # --- LISTA ---
    lista_view = ft.ListView(expand=True, spacing=10, padding=20)

    def atualizar_lista():
        lista_view.controls.clear()
        dados = db.listar_contratos()
        for d in dados:
            rid, emp, num, ven, total, s_ant, desc, d_ini = d
            g_db = db.obter_gastos(rid)
            saldo_r = total - s_ant - sum(g_db.values())
            
            st_v = calcular_status_vencimento(ven)
            st_s = calcular_status_saldo(saldo_r)

            lista_view.controls.append(
                ft.Container(
                    bgcolor="white", padding=15, border_radius=12,
                    on_click=lambda e, dt=d: abrir_detalhes(dt),
                    border=ft.border.only(left=ft.BorderSide(6, st_v["cor"])),
                    content=ft.Row([
                        ft.Icon(ft.icons.FILE_COPY_ROUNDED, color="blue_grey"),
                        ft.Column([
                            ft.Text(emp.upper(), weight="bold"),
                            ft.Row([
                                ft.Container(ft.Text(st_v["label"], size=9, color="white"), bgcolor=st_v["cor"], padding=5, border_radius=4),
                                ft.Container(ft.Text(st_s["label"], size=9, color="white"), bgcolor=st_s["cor"], padding=5, border_radius=4)
                            ])
                        ], expand=True),
                        ft.Text(formatar_moeda(saldo_r), weight="bold", color="green" if saldo_r > 25000 else "red"),
                        ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color="red_300", on_click=lambda e, r=rid: (db.deletar_contrato(r), atualizar_lista()))
                    ])
                )
            )
        page.update()

    # --- VIEW ---
    page.views.append(
        ft.View(
            "/dashboard",
            [
                ft.AppBar(title=ft.Text("Gestão de Contratos"), center_title=True, bgcolor="white",
                          actions=[ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: page.go("/"))]),
                lista_view,
                ft.FloatingActionButton(content=ft.Icon(ft.icons.ADD, color="white"), 
                                        on_click=lambda _: (setattr(modal_add, "open", True), page.update()), bgcolor="blue")
            ],
            bgcolor="#F0F2F5"
        )
    )
    atualizar_lista()