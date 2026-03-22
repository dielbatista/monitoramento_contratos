import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt

def conectar():
    db_type = os.getenv("DB_TYPE", "sqlite")
    if db_type == "postgres":
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database=os.getenv("DB_NAME", "contratos_db"),
            user=os.getenv("DB_USER", "user_admin"),
            password=os.getenv("DB_PASS", "senha_segura_123"),
            port=os.getenv("DB_PORT", "5432")
        )
    else:
        conn = sqlite3.connect("contratos.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()
    db_is_postgres = os.getenv("DB_TYPE") == "postgres"
    
    # --- TABELA DE USUÁRIOS (CASE-SENSITIVE) ---
    if db_is_postgres:
        # No Postgres, a diferenciação é padrão.
        cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, usuario TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, is_admin INTEGER DEFAULT 0)")
    else:
        # No SQLite, usamos COLLATE BINARY para diferenciar 'Diel' de 'diel'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                usuario TEXT UNIQUE NOT NULL COLLATE BINARY, 
                senha TEXT NOT NULL, 
                is_admin INTEGER DEFAULT 0
            )
        """)

    # --- TABELA DE CONTRATOS ---
    if db_is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contratos (
                id SERIAL PRIMARY KEY,
                empresa TEXT NOT NULL,
                n_contrato TEXT,
                data_inicio TEXT,
                data_fim TEXT,
                valor_total REAL,
                valor_gasto_anterior REAL
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa TEXT NOT NULL,
                n_contrato TEXT,
                data_inicio TEXT,
                data_fim TEXT,
                valor_total REAL,
                valor_gasto_anterior REAL
            )
        """)

    # --- TABELA DE GASTOS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos_mensais (
            contrato_id INTEGER,
            mes INTEGER,
            valor REAL,
            PRIMARY KEY (contrato_id, mes)
        )
    """)

    # Admin padrão (sempre criado em minúsculo por convenção)
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        senha_hash = bcrypt.hashpw("p3dr0d4v1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sql = "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (%s, %s, %s)" if db_is_postgres else \
              "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (?, ?, ?)"
        cursor.execute(sql, ("admin", senha_hash, 1))

    conn.commit()
    conn.close()

# --- FUNÇÕES DE USUÁRIO (SENSÍVEIS A MAIÚSCULAS) ---

def verificar_se_admin(usuario):
    conn = conectar()
    cursor = conn.cursor()
    # O strip() remove apenas espaços acidentais, mantendo as letras originais
    sql = "SELECT is_admin FROM usuarios WHERE usuario = %s" if os.getenv("DB_TYPE") == "postgres" else \
          "SELECT is_admin FROM usuarios WHERE usuario = ? COLLATE BINARY"
    cursor.execute(sql, (usuario.strip(),))
    row = cursor.fetchone()
    conn.close()
    return bool(row[0]) if row else False

def criar_usuario(usuario, senha_plana, is_admin):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Removemos o .lower() para salvar exatamente como foi digitado
        usuario_limpo = usuario.strip()
        senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_int = 1 if is_admin else 0
        
        sql = "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (%s, %s, %s)" if os.getenv("DB_TYPE") == "postgres" else \
              "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (?, ?, ?)"
        
        cursor.execute(sql, (usuario_limpo, senha_hash, admin_int))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False
    finally:
        conn.close()

def verificar_login(usuario, senha_plana):
    conn = conectar()
    usuario_input = usuario.strip() # Mantém maiúsculas/minúsculas
    
    if os.getenv("DB_TYPE") == "postgres":
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario_input,))
    else:
        cursor = conn.cursor()
        # Forçamos a comparação binária para validar o login
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? COLLATE BINARY", (usuario_input,))
        
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
    try:
        sql = """INSERT INTO contratos (empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio) 
                 VALUES (%s, %s, %s, %s, %s, %s)""" if os.getenv("DB_TYPE") == "postgres" else \
              """INSERT INTO contratos (empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio) 
                 VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (empresa.upper(), n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def listar_contratos():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute("SELECT id, empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio FROM contratos ORDER BY id DESC")
    rows = cursor.fetchall(); conn.close()
    return [tuple(row) for row in rows]

def obter_gastos(contrato_id):
    conn = conectar(); cursor = conn.cursor()
    sql = "SELECT mes, valor FROM gastos_mensais WHERE contrato_id = %s" if os.getenv("DB_TYPE") == "postgres" else "SELECT mes, valor FROM gastos_mensais WHERE contrato_id = ?"
    cursor.execute(sql, (contrato_id,))
    rows = cursor.fetchall(); conn.close()
    return {row[0]: row[1] for row in rows}

def registrar_gasto(c_id, mes, valor):
    conn = conectar(); cursor = conn.cursor()
    if os.getenv("DB_TYPE") == "postgres":
        sql = "INSERT INTO gastos_mensais (contrato_id, mes, valor) VALUES (%s, %s, %s) ON CONFLICT (contrato_id, mes) DO UPDATE SET valor = EXCLUDED.valor"
    else:
        sql = "INSERT OR REPLACE INTO gastos_mensais (contrato_id, mes, valor) VALUES (?, ?, ?)"
    cursor.execute(sql, (c_id, mes, valor))
    conn.commit(); conn.close()

def deletar_contrato(c_id):
    conn = conectar(); cursor = conn.cursor()
    sql = "DELETE FROM contratos WHERE id = %s" if os.getenv("DB_TYPE") == "postgres" else "DELETE FROM contratos WHERE id = ?"
    cursor.execute(sql, (c_id,))
    conn.commit(); conn.close()