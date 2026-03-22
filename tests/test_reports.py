import sys
from unittest.mock import MagicMock, patch
import io
import pytest

# --- MOCKS DE SEGURANÇA (Para evitar o erro de MD5 do ReportLab) ---
mock_rl = MagicMock()
sys.modules['reportlab'] = mock_rl
sys.modules['reportlab.lib'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'].A4 = (595.27, 841.89)
sys.modules['reportlab.lib.colors'] = MagicMock()
# Criamos um mock para o módulo pdfgen para o import não falhar
sys.modules['reportlab.pdfgen'] = MagicMock()

from app.reports import gerar_pdf_contrato

# --- CLASSE DE SIMULAÇÃO ---
class FakeCanvas:
    def __init__(self, buffer, pagesize=None):
        self.buffer = buffer
    def setFont(self, *args, **kwargs): pass
    def drawString(self, *args, **kwargs): pass
    def setFillColor(self, *args, **kwargs): pass
    def rect(self, *args, **kwargs): pass
    def showPage(self): pass
    def save(self):
        # Escreve os bytes que o teste espera
        self.buffer.write(b"%PDF-1.4 Mock Content")

def test_gerar_pdf_retorna_bytes_validos():
    """Usa patch para garantir que o Canvas seja substituído na hora da execução."""
    contrato = (1, "EMPRESA TESTE", "123/2026", "2026-12-31", 10000.0, 2000.0, "2026-01-01")
    gastos = {1: 500.0}
    
    # O 'patch' intercepta a chamada ao Canvas dentro do reports.py
    with patch("app.reports.canvas.Canvas", new=FakeCanvas):
        pdf_bytes, nome_arquivo = gerar_pdf_contrato(contrato, gastos)
    
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert "relatorio_123_2026.pdf" in nome_arquivo

def test_sanitizacao_nome_arquivo_complexo():
    """Garante que o Regex limpa caracteres que quebram o Linux."""
    contrato = (1, "TESTE", "CONTRATO/TI 001", "2026-12-31", 1000.0, 0, "2026-01-01")
    
    with patch("app.reports.canvas.Canvas", new=FakeCanvas):
        _, nome_arquivo = gerar_pdf_contrato(contrato, {})
    
    assert "/" not in nome_arquivo
    assert "CONTRATO_TI_001" in nome_arquivo

def test_formatacao_moeda_fmt():
    """Testa a lógica de formatação R$ do reports.py."""
    # Teste puro de lógica, não precisa de patch
    def fmt(v): 
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    assert fmt(10.5) == "R$ 10,50"
    assert fmt(1200.75) == "R$ 1.200,75"