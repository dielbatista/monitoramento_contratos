import sqlite3

def init_db():
    conn = sqlite3.connect("contratos.db")
    cursor = conn.cursor()
    
    # Criando a tabela com o nome 'numero' para evitar o erro de coluna inexistente
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT,
            numero TEXT,
            data_vencimento TEXT,
            valor_total REAL,
            saldo_anterior REAL,
            descricao TEXT,
            data_inicio TEXT
        )
    """)

    # Tabela de gastos mensais vinculada ao contrato
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrato_id INTEGER,
            mes INTEGER,
            valor REAL,
            FOREIGN KEY(contrato_id) REFERENCES contratos(id)
        )
    """)
    
    conn.commit()
    conn.close()

def adicionar_contrato(empresa, numero, vencimento, total, saldo_ant, desc, data_inicio):
    conn = sqlite3.connect("contratos.db")
    cursor = conn.cursor()
    # O comando INSERT deve usar exatamente os nomes das colunas do CREATE TABLE
    cursor.execute("""
        INSERT INTO contratos (empresa, numero, data_vencimento, valor_total, saldo_anterior, descricao, data_inicio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (empresa, numero, vencimento, total, saldo_ant, desc, data_inicio))
    conn.commit()
    conn.close()

def listar_contratos():
    conn = sqlite3.connect("contratos.db")
    cursor = conn.cursor()
    # Selecionamos as 8 colunas na ordem que o Dashboard espera receber
    cursor.execute("""
        SELECT id, empresa, numero, data_vencimento, valor_total, saldo_anterior, descricao, data_inicio 
        FROM contratos
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados

def deletar_contrato(contrato_id):
    conn = sqlite3.connect("contratos.db")
    cursor = conn.cursor()
    # Deleta primeiro os gastos para manter a integridade referencial
    cursor.execute("DELETE FROM gastos WHERE contrato_id = ?", (contrato_id,))
    cursor.execute("DELETE FROM contratos WHERE id = ?", (contrato_id,))
    conn.commit()
    conn.close()

def registrar_gasto(contrato_id, mes, valor):
    conn = sqlite3.connect("contratos.db")
    cursor = conn.cursor()
    # Lógica de UPSERT (Update ou Insert) manual para SQLite
    cursor.execute("SELECT id FROM gastos WHERE contrato_id = ? AND mes = ?", (contrato_id, mes))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE gastos SET valor = ? WHERE id = ?", (valor, row[0]))
    else:
        cursor.execute("INSERT INTO gastos (contrato_id, mes, valor) VALUES (?, ?, ?)", (contrato_id, mes, valor))
    conn.commit()
    conn.close()

def obter_gastos(contrato_id):
    conn = sqlite3.connect("contratos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT mes, valor FROM gastos WHERE contrato_id = ?", (contrato_id,))
    # Transforma em dicionário {mês: valor} para facilitar o preenchimento dos TextFields
    gastos = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return gastos