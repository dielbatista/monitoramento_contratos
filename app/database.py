import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

def conectar():
    db_type = os.getenv("DB_TYPE", "sqlite")
    if db_type == "postgres":
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "contratos_db"),
            user=os.getenv("DB_USER", "user_admin"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "5432")
        )
    else:
        conn = sqlite3.connect("contratos.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def limpar_valor_monetario(valor):
    if valor is None or str(valor).strip() == "":
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(texto)
    except ValueError:
        return 0.0

def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()
    db_is_postgres = os.getenv("DB_TYPE") == "postgres"
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS usuarios (
            id {'SERIAL PRIMARY KEY' if db_is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'}, 
            usuario TEXT UNIQUE NOT NULL, 
            senha TEXT NOT NULL, 
            is_admin INTEGER DEFAULT 0
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS contratos (
            id {'SERIAL PRIMARY KEY' if db_is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            empresa TEXT NOT NULL,
            n_contrato TEXT,
            data_inicio TEXT,
            data_fim TEXT,
            valor_total REAL,
            valor_gasto_anterior REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos_mensais (
            contrato_id INTEGER,
            mes INTEGER,
            valor REAL,
            PRIMARY KEY (contrato_id, mes)
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS aditivos (
            id {'SERIAL PRIMARY KEY' if db_is_postgres else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            contrato_id INTEGER,
            numero_aditivo TEXT,
            data_assinatura TEXT,
            novo_vencimento TEXT,
            valor_aditivo REAL,
            descricao TEXT,
            FOREIGN KEY (contrato_id) REFERENCES contratos (id) ON DELETE CASCADE
        )
    """)

    try:
        check_sql = "SELECT id FROM usuarios WHERE usuario = %s" if db_is_postgres else "SELECT id FROM usuarios WHERE usuario = 'admin'"
        if db_is_postgres: cursor.execute(check_sql, ("admin",))
        else: cursor.execute(check_sql)
            
        if not cursor.fetchone():
            senha_hash = bcrypt.hashpw("p3dr0d4v1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            insert_sql = "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (%s, %s, %s)" if db_is_postgres else \
                         "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (?, ?, ?)"
            cursor.execute(insert_sql, ("admin", senha_hash, 1))
    except Exception as e:
        print(f"Aviso admin: {e}")

    conn.commit()
    conn.close()

# --- FUNÇÕES DE USUÁRIO ---

def verificar_se_admin(usuario):
    conn = conectar()
    cursor = conn.cursor()
    is_pg = os.getenv("DB_TYPE") == "postgres"
    sql = "SELECT is_admin FROM usuarios WHERE usuario = %s" if is_pg else "SELECT is_admin FROM usuarios WHERE usuario = ?"
    cursor.execute(sql, (usuario.strip(),))
    row = cursor.fetchone()
    conn.close()
    return bool(row[0]) if row else False

def criar_usuario(usuario, senha_plana, is_admin):
    conn = conectar()
    cursor = conn.cursor()
    try:
        senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        is_pg = os.getenv("DB_TYPE") == "postgres"
        sql = "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (%s, %s, %s)" if is_pg else \
              "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (?, ?, ?)"
        cursor.execute(sql, (usuario.strip(), senha_hash, 1 if is_admin else 0))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def verificar_login(usuario, senha_plana):
    conn = conectar()
    usuario_input = usuario.strip()
    is_pg = os.getenv("DB_TYPE") == "postgres"
    if is_pg:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario_input,))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario_input,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_dict = dict(row)
        if bcrypt.checkpw(senha_plana.encode('utf-8'), user_dict["senha"].encode('utf-8')):
            return {"valido": True, "is_admin": bool(user_dict["is_admin"])}
    return {"valido": False}

# --- FUNÇÕES DE CONTRATOS ---

def adicionar_contrato(empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio):
    conn = conectar()
    cursor = conn.cursor()
    v_total = limpar_valor_monetario(valor_total)
    v_ant = limpar_valor_monetario(valor_gasto_anterior)
    is_pg = os.getenv("DB_TYPE") == "postgres"
    try:
        sql = "INSERT INTO contratos (empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio) VALUES (%s, %s, %s, %s, %s, %s)" if is_pg else \
              "INSERT INTO contratos (empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (empresa.upper(), n_contrato, data_fim, v_total, v_ant, data_inicio))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar contrato: {e}")
        return False
    finally: conn.close()

def listar_contratos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio FROM contratos ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [tuple(row) for row in rows]

# --- FUNÇÃO DE ADITIVO CORRIGIDA (AGORA SALVA NO HISTÓRICO E ATUALIZA O CONTRATO) ---
def atualizar_contrato_aditivo(c_id, novo_total, nova_data, valor_somado):
    conn = conectar()
    cursor = conn.cursor()
    is_pg = os.getenv("DB_TYPE") == "postgres"
    
    try:
        from datetime import date
        hoje = date.today().strftime("%d-%m-%Y")

        # --- NOVA LÓGICA: Descobre qual o próximo número do aditivo ---
        sql_count = "SELECT COUNT(*) FROM aditivos WHERE contrato_id = %s" if is_pg else \
                    "SELECT COUNT(*) FROM aditivos WHERE contrato_id = ?"
        cursor.execute(sql_count, (c_id,))
        total_aditivos = cursor.fetchone()[0]
        proximo_numero = total_aditivos + 1  # Se tinha 0, esse será o 1.

        # 1. Registra o histórico incluindo o NUMERO_ADITIVO
        sql_hist = """INSERT INTO aditivos (contrato_id, numero_aditivo, valor_aditivo, novo_vencimento, descricao, data_assinatura) 
                      VALUES (%s, %s, %s, %s, %s, %s)""" if is_pg else \
                   """INSERT INTO aditivos (contrato_id, numero_aditivo, valor_aditivo, novo_vencimento, descricao, data_assinatura) 
                      VALUES (?, ?, ?, ?, ?, ?)"""
        
        # Adicionamos 'proximo_numero' na execução
        cursor.execute(sql_hist, (c_id, proximo_numero, valor_somado, nova_data, "Aditivo de Valor/Prazo", hoje))

        # 2. Atualiza os valores principais na tabela contratos
        sql_upd = "UPDATE contratos SET valor_total = %s, data_fim = %s WHERE id = %s" if is_pg else \
                  "UPDATE contratos SET valor_total = ?, data_fim = ? WHERE id = ?"
        
        cursor.execute(sql_upd, (novo_total, nova_data, c_id))
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao atualizar aditivo: {e}")
        conn.rollback()
    finally:
        conn.close()

def deletar_contrato(c_id):
    conn = conectar()
    cursor = conn.cursor()
    is_pg = os.getenv("DB_TYPE") == "postgres"
    params = (c_id,)
    cursor.execute("DELETE FROM gastos_mensais WHERE contrato_id = " + ("%s" if is_pg else "?"), params)
    cursor.execute("DELETE FROM aditivos WHERE contrato_id = " + ("%s" if is_pg else "?"), params)
    cursor.execute("DELETE FROM contratos WHERE id = " + ("%s" if is_pg else "?"), params)
    conn.commit()
    conn.close()

# --- GASTOS ---
def registrar_gasto(c_id, mes, valor):
    valor_limpo = limpar_valor_monetario(valor)
    conn = conectar()
    cursor = conn.cursor()
    is_pg = os.getenv("DB_TYPE") == "postgres"
    if is_pg:
        sql = "INSERT INTO gastos_mensais (contrato_id, mes, valor) VALUES (%s, %s, %s) ON CONFLICT (contrato_id, mes) DO UPDATE SET valor = EXCLUDED.valor"
    else:
        sql = "INSERT OR REPLACE INTO gastos_mensais (contrato_id, mes, valor) VALUES (?, ?, ?)"
    cursor.execute(sql, (c_id, mes, valor_limpo))
    conn.commit()
    conn.close()

def obter_gastos(contrato_id):
    conn = conectar()
    cursor = conn.cursor()
    is_pg = os.getenv("DB_TYPE") == "postgres"
    sql = "SELECT mes, valor FROM gastos_mensais WHERE contrato_id = %s" if is_pg else "SELECT mes, valor FROM gastos_mensais WHERE contrato_id = ?"
    cursor.execute(sql, (contrato_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def listar_aditivos(contrato_id):
    conn = conectar()
    cursor = conn.cursor()
    is_pg = os.getenv("DB_TYPE") == "postgres"
    sql = "SELECT * FROM aditivos WHERE contrato_id = %s" if is_pg else "SELECT * FROM aditivos WHERE contrato_id = ?"
    cursor.execute(sql, (contrato_id,))
    dados = cursor.fetchall()
    conn.close()
    return dados