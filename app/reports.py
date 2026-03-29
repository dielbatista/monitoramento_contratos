import re
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def gerar_pdf_contrato(contrato_dados, gastos_mensais):
    """
    Gera um relatório PDF detalhado incluindo Valor Inicial, Aditivos e Saldo Atual.
    contrato_dados esperado: (id, empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio, valor_aditivo)
    """
    # 1. Preparação do buffer em memória
    buffer = io.BytesIO()
    
    # 2. Configuração do Canvas
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Utilitário de Formatação de Moeda ---
    def fmt(v): 
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # --- Extração de Dados (8 elementos conforme sua nova lógica) ---
    empresa = contrato_dados[1]
    num_contrato = contrato_dados[2]
    data_fim = contrato_dados[3]
    valor_inicial = contrato_dados[4]
    gasto_anterior = contrato_dados[5]
    data_inicio = contrato_dados[6]
    valor_aditivo = contrato_dados[7] # Novo campo
    
    # Cálculos Financeiros
    total_gasto_atual = sum(gastos_mensais.values())
    valor_global = valor_inicial + valor_aditivo
    gasto_total_acumulado = gasto_anterior + total_gasto_atual
    saldo_restante = valor_global - gasto_total_acumulado

    # --- Cabeçalho ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"RELATÓRIO DE CONTRATO: {empresa}")
    
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 75, f"Nº Contrato: {num_contrato}")
    c.drawString(50, height - 90, f"Período de Vigência: {data_inicio} até {data_fim}")

    # --- Quadro de Resumo Financeiro ---
    c.setFillColor(colors.whitesmoke)
    c.rect(50, height - 200, 500, 95, fill=1)
    c.setFillColor(colors.black)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(65, height - 120, "RESUMO FINANCEIRO DO CONTRATO")
    
    c.setFont("Helvetica", 10)
    c.drawString(65, height - 140, f"Valor Inicial: {fmt(valor_inicial)}")
    
    # Destaque para o Aditivo
    c.setFillColor(colors.blue)
    c.drawString(65, height - 155, f"(+) Aditivos Acumulados: {fmt(valor_aditivo)}")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(65, height - 170, f"(=) Valor Global Atualizado: {fmt(valor_global)}")
    
    c.setFont("Helvetica", 10)
    c.drawString(65, height - 185, f"(-) Gasto Total (Anteriores + Atual): {fmt(gasto_total_acumulado)}")
    
    # Destaque para o Saldo
    if saldo_restante < 10000:
        c.setFillColor(colors.red)
    else:
        c.setFillColor(colors.darkgreen)
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(330, height - 185, f"SALDO DISPONÍVEL: {fmt(saldo_restante)}")
    
    c.setFillColor(colors.black)

    # --- Lista de Gastos Mensais ---
    c.setFont("Helvetica-Bold", 12)
    y_lista = height - 230
    c.drawString(50, y_lista, "Detalhamento de Gastos Mensais (Exercício Atual):")
    c.line(50, y_lista - 5, 550, y_lista - 5)

    y = y_lista - 30
    c.setFont("Helvetica", 10)
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    for i, nome in enumerate(meses_nomes, 1):
        valor = gastos_mensais.get(i, 0.0)
        if i % 2 == 0:
            c.setFillColor(colors.whitesmoke)
            c.rect(50, y - 5, 500, 15, fill=1)
            c.setFillColor(colors.black)
            
        c.drawString(70, y, f"{nome}:")
        c.drawRightString(530, y, fmt(valor))
        y -= 20
        
    # Rodapé
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.grey)
    c.drawString(50, 30, f"Relatório gerado em: {hoje}")

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    num_limpo = re.sub(r'[^\w\-]', '_', str(num_contrato))
    nome_sugerido = f"relatorio_contrato_{num_limpo}.pdf"

    return pdf_bytes, nome_sugerido