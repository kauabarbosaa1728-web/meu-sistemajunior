from werkzeug.security import generate_password_hash
from psycopg2 import pool

# 🔌 CONEXÃO COM NEON
db_pool = pool.SimpleConnectionPool(
    1, 10,
    host="ep-calm-moon-acucwei3-pooler.sa-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_zGebRqQWoB06",
    port="5432",
    sslmode="require"
)

# ================= CONECTAR =================
def conectar():
    return db_pool.getconn()

# ================= DEVOLVER CONEXÃO =================
def devolver_conexao(conn):
    if conn:
        db_pool.putconn(conn)

# ================= LOG =================
def registrar_log(usuario, acao, detalhes=""):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO logs (usuario, acao, detalhes)
        VALUES (%s, %s, %s)
        """, (usuario, acao, detalhes))

        conn.commit()
    except Exception as e:
        print("Erro ao registrar log:", e)
    finally:
        devolver_conexao(conn)

# ================= PERMISSÕES =================
def permissoes_por_plano(plano):
    plano = (plano or "").lower()

    if plano == "premium":
        return {
            "pode_estoque": 1,
            "pode_transferencia": 1,
            "pode_historico": 1,
            "pode_usuarios": 0,
            "pode_editar_estoque": 1,
            "pode_excluir_estoque": 1,
            "pode_logs": 0
        }

    if plano == "profissional":
        return {
            "pode_estoque": 1,
            "pode_transferencia": 1,
            "pode_historico": 1,
            "pode_usuarios": 0,
            "pode_editar_estoque": 1,
            "pode_excluir_estoque": 0,
            "pode_logs": 0
        }

    return {
        "pode_estoque": 1,
        "pode_transferencia": 0,
        "pode_historico": 1,
        "pode_usuarios": 0,
        "pode_editar_estoque": 0,
        "pode_excluir_estoque": 0,
        "pode_logs": 0
    }

# ================= CRIAR BANCO =================
def criar_banco():
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        # 🔹 USUÁRIOS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            senha TEXT,
            cargo TEXT,
            online INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            pode_estoque INTEGER DEFAULT 0,
            pode_transferencia INTEGER DEFAULT 0,
            pode_historico INTEGER DEFAULT 0,
            pode_usuarios INTEGER DEFAULT 0,
            pode_editar_estoque INTEGER DEFAULT 0,
            pode_excluir_estoque INTEGER DEFAULT 0,
            pode_logs INTEGER DEFAULT 0,
            email TEXT,
            plano TEXT DEFAULT 'basico',
            nome_empresa TEXT
        )
        """)

        # 🔹 LOGS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            usuario TEXT,
            acao TEXT,
            detalhes TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 🔹 PAGAMENTOS (PIX)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id SERIAL PRIMARY KEY,
            usuario TEXT,
            email TEXT,
            senha TEXT,
            nome_empresa TEXT,
            plano TEXT,
            status TEXT DEFAULT 'pendente',
            pagamento_id TEXT
        )
        """)

        # 🔹 ADMIN PADRÃO
        cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", ("admin",))
        admin = cursor.fetchone()

        if not admin:
            cursor.execute("""
            INSERT INTO usuarios (usuario, senha, cargo, ativo)
            VALUES (%s, %s, 'admin', 1)
            """, ("admin", generate_password_hash("admin123")))

        conn.commit()

    except Exception as e:
        print("Erro ao criar banco:", e)
        if conn:
            conn.rollback()

    finally:
        devolver_conexao(conn)
