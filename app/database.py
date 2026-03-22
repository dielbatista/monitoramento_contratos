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
    
    # Tabela de Usuários (Note o is_admin como INTEGER para compatibilidade)
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, usuario TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, is_admin INTEGER DEFAULT 0)")

    # Tabela de Contratos
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

    # Tabela de Gastos Mensais
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos_mensais (
            contrato_id INTEGER,
            mes INTEGER,
            valor REAL,
            PRIMARY KEY (contrato_id, mes)
        )
    """)

    # Lógica de Auto-Admin
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        senha_plana = "p3dr0d4v1"
        senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        sql = "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (%s, %s, %s)" if os.getenv("DB_TYPE") == "postgres" \
              else "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (?, ?, ?)"
        cursor.execute(sql, ("admin", senha_hash, 1))
        print(">>> ADMIN CRIADO: p3dr0d4v1")

    conn.commit()
    conn.close()

# --- NOVAS FUNÇÕES DE GERENCIAMENTO DE USUÁRIOS ---

def verificar_se_admin(usuario):
    """Retorna True se o usuário logado for administrador."""
    conn = conectar()
    cursor = conn.cursor()
    sql = "SELECT is_admin FROM usuarios WHERE usuario = %s" if os.getenv("DB_TYPE") == "postgres" else \
          "SELECT is_admin FROM usuarios WHERE usuario = ?"
    cursor.execute(sql, (usuario,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # No SQLite retorna 1/0, no Postgres depende do driver, aqui tratamos como verdade
        return bool(row[0])
    return False

def criar_usuario(usuario, senha_plana, is_admin):
    """Cria um novo usuário com senha criptografada."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_int = 1 if is_admin else 0
        
        sql = "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (%s, %s, %s)" if os.getenv("DB_TYPE") == "postgres" else \
              "INSERT INTO usuarios (usuario, senha, is_admin) VALUES (?, ?, ?)"
        
        cursor.execute(sql, (usuario, senha_hash, admin_int))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False
    finally:
        conn.close()

# --- FUNÇÕES DE CONTRATOS (MANTIDAS) ---

def adicionar_contrato(empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio):
    conn = conectar()
    cursor = conn.cursor()
    try:
        sql = """INSERT INTO contratos (empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio) 
                 VALUES (%s, %s, %s, %s, %s, %s)""" if os.getenv("DB_TYPE") == "postgres" else \
              """INSERT INTO contratos (empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio) 
                 VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar: {e}")
        return False
    finally: conn.close()

def listar_contratos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, empresa, n_contrato, data_fim, valor_total, valor_gasto_anterior, data_inicio FROM contratos ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [tuple(row) for row in rows]

def obter_gastos(contrato_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT mes, valor FROM gastos_mensais WHERE contrato_id = %s" if os.getenv("DB_TYPE") == "postgres" else "SELECT mes, valor FROM gastos_mensais WHERE contrato_id = ?", (contrato_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def registrar_gasto(c_id, mes, valor):
    conn = conectar()
    cursor = conn.cursor()
    if os.getenv("DB_TYPE") == "postgres":
        sql = "INSERT INTO gastos_mensais (contrato_id, mes, valor) VALUES (%s, %s, %s) ON CONFLICT (contrato_id, mes) DO UPDATE SET valor = EXCLUDED.valor"
    else:
        sql = "INSERT OR REPLACE INTO gastos_mensais (contrato_id, mes, valor) VALUES (?, ?, ?)"
    cursor.execute(sql, (c_id, mes, valor))
    conn.commit()
    conn.close()

def deletar_contrato(c_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contratos WHERE id = %s" if os.getenv("DB_TYPE") == "postgres" else "DELETE FROM contratos WHERE id = ?", (c_id,))
    conn.commit()
    conn.close()

def verificar_login(usuario, senha_plana):
    conn = conectar()
    if os.getenv("DB_TYPE") == "postgres":
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_dict = dict(row)
        if bcrypt.checkpw(senha_plana.encode('utf-8'), user_dict["senha"].encode('utf-8')):
            return {"valido": True, "is_admin": user_dict["is_admin"]}
    return {"valido": False}