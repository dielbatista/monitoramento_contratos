import sys
import os
import io
from unittest.mock import MagicMock, patch

# 1. MOCKS DO REPORTLAB (Configuração do ambiente)
mock_rl = MagicMock()
sys.modules['reportlab'] = mock_rl
sys.modules['reportlab.lib'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'].A4 = (595.27, 841.89)
sys.modules['reportlab.lib.colors'] = MagicMock()
sys.modules['reportlab.pdfgen'] = MagicMock()
sys.modules['reportlab.pdfgen.canvas'] = MagicMock()

# 2. DEFINIÇÃO DA CLASSE FAKE
class FakeCanvas:
    def __init__(self, buffer, pagesize=None):
        self.buffer = buffer
    def setFont(self, *args, **kwargs): pass
    def drawString(self, *args, **kwargs): pass
    def drawRightString(self, *args, **kwargs): pass
    def setFillColor(self, *args, **kwargs): pass
    def setLineWidth(self, *args, **kwargs): pass
    def line(self, *args, **kwargs): pass
    def rect(self, *args, **kwargs): pass
    def showPage(self): pass
    def save(self):
        # Escreve bytes reais no buffer para o getvalue() funcionar
        if hasattr(self.buffer, 'write'):
            self.buffer.write(b"%PDF-1.4 Mock Content")

# 3. GARANTIR O PATH E IMPORTAR
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app.reports

# 4. TESTES
def test_gerar_pdf_retorna_bytes_validos():
    """Testa o retorno básico da função."""
    contrato = (1, "EMPRESA", "123", "2026-12-31", 1000.0, 0.0, "2026-01-01", 0.0)
    gastos = {1: 100.0}
    
    # Patch direto no módulo importado
    with patch("app.reports.canvas.Canvas", new=FakeCanvas):
        # Chamamos via módulo para garantir consistência
        res = app.reports.gerar_pdf_contrato(contrato, gastos)
    
    assert res is not None, "A função retornou None!"
    pdf_bytes, nome = res
    assert pdf_bytes.startswith(b"%PDF")
    assert "123" in nome

def test_sanitizacao_nome_arquivo_complexo():
    """Testa a regex de limpeza do nome."""
    contrato = (1, "TESTE", "ABC/999", "2026", 100.0, 0.0, "2026", 0.0)
    
    with patch("app.reports.canvas.Canvas", new=FakeCanvas):
        _, nome = app.reports.gerar_pdf_contrato(contrato, {})
    
    assert "/" not in nome
    assert "ABC_999" in nome

def test_formatacao_moeda_fmt_logica():
    """Testa a lógica de formatação R$ que está dentro da função."""
    # Como fmt() é interna, testamos se a função roda sem erro com valores decimais
    contrato = (1, "TESTE", "1", "2026", 1250.50, 0.0, "2026", 0.0)
    
    with patch("app.reports.canvas.Canvas", new=FakeCanvas):
        pdf_bytes, _ = app.reports.gerar_pdf_contrato(contrato, {})
    
    assert len(pdf_bytes) > 0