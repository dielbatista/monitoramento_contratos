import re
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def gerar_pdf_contrato(contrato_dados, gastos_mensais):
    # 1. Preparação do buffer em memória (Crucial para ambientes Docker)
    buffer = io.BytesIO()
    
    # 2. Configuração do Canvas apontando para o buffer
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Cabeçalho ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"RELATÓRIO DE CONTRATO: {contrato_dados[1]}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Nº Contrato: {contrato_dados[2]}")
    c.drawString(50, height - 100, f"Vigência: {contrato_dados[6]} até {contrato_dados[3]}")

    # --- Tabela de Resumo Financeiro ---
    c.setFillColor(colors.whitesmoke)
    c.rect(50, height - 180, 500, 60, fill=1)
    c.setFillColor(colors.black)
    
    total = contrato_dados[4]
    gasto_ant = contrato_dados[5]
    gasto_atual = sum(gastos_mensais.values())
    saldo = total - gasto_ant - gasto_atual

    # Formatação de moeda para o PDF
    def fmt(v): 
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    c.drawString(60, height - 140, f"Valor Total: {fmt(total)}")
    c.drawString(60, height - 160, f"Saldo Atual: {fmt(saldo)}")

    # --- Lista de Gastos Mensais ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 210, "Detalhamento de Gastos Mensais (Ano Atual):")
    
    y = height - 240
    c.setFont("Helvetica", 10)
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    for i, nome in enumerate(meses_nomes, 1):
        valor = gastos_mensais.get(i, 0.0)
        c.drawString(70, y, f"{nome}: {fmt(valor)}")
        y -= 20
        
        # Controle de nova página
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    # Finaliza o PDF no buffer
    c.save()
    
    # 3. Recupera os bytes e limpa o buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    # 4. Sanitização rigorosa do nome do arquivo
    # Substitui qualquer caractere que não seja letra, número ou hífen por '_'
    # Isso resolve o erro de "No such file" causado pela barra '/' do contrato
    num_limpo = re.sub(r'[^\w\-]', '_', str(contrato_dados[2]))
    nome_sugerido = f"relatorio_{num_limpo}.pdf"

    # Retorna os dados binários para o base64 e o nome para o navegador
    return pdf_bytes, nome_sugerido