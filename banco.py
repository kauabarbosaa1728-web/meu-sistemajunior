from werkzeug.security import generate_password_hash
from psycopg2 import pool

# ================= POOL =================
db_pool = None

def criar_pool():
    global db_pool
    try:
        db_pool = pool.SimpleConnectionPool(
            1, 10,
            host="ep-calm-moon-acucwei3-pooler.sa-east-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_zGebRqQWoB06",
            port="5432",
            sslmode="require"
        )
        print("✅ Pool criado com sucesso")
    except Exception as e:
        print("❌ ERRO AO CRIAR POOL:", e)
        db_pool = None

criar_pool()

# ================= CONEXÃO =================
def conectar():
    global db_pool
    try:
        if db_pool is None:
            criar_pool()

        conn = db_pool.getconn()

        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()

        return conn

    except Exception as e:
        print("❌ ERRO AO CONECTAR:", e)
        db_pool = None
        return None


def devolver_conexao(conn):
    global db_pool
    try:
        if conn and db_pool:
            db_pool.putconn(conn)
    except Exception as e:
        print("Erro ao devolver conexão:", e)


# ================= LOG =================
def registrar_log(usuario, acao, detalhes=""):
    conn = None
    try:
        conn = conectar()
        if conn is None:
            return

        cursor = conn.cursor()

        cursor.execute("""
        SELECT empresa_id FROM usuarios WHERE usuario=%s
        """, (usuario,))
        emp = cursor.fetchone()
        empresa_id = emp[0] if emp else None

        cursor.execute("""
        INSERT INTO logs (usuario, acao, detalhes, empresa_id)
        VALUES (%s, %s, %s, %s)
        """, (usuario, acao, detalhes, empresa_id))

        conn.commit()

    except Exception as e:
        print("Erro ao registrar log:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            devolver_conexao(conn)


# ================= BANCO =================
def criar_banco():
    conn = None
    try:
        conn = conectar()
        if conn is None:
            print("❌ Sem conexão com banco")
            return

        cursor = conn.cursor()

        # 🔥 USUARIOS
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

        # 🔥 GARANTE COLUNA (ANTES DE USAR)
        cursor.execute("""
        ALTER TABLE usuarios 
        ADD COLUMN IF NOT EXISTS empresa_id TEXT
        """)

        # 🔥 PAGAMENTOS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id SERIAL PRIMARY KEY,
            usuario TEXT UNIQUE,
            email TEXT,
            senha TEXT,
            nome_empresa TEXT,
            plano TEXT,
            status TEXT,
            pagamento_id TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vencimento TIMESTAMP
        )
        """)

        cursor.execute("""
        ALTER TABLE pagamentos 
        ADD COLUMN IF NOT EXISTS empresa_id TEXT
        """)

        # 🔥 OUTRAS TABELAS
        tabelas = ["estoque", "transferencias", "logs", "financeiro", "vendas"]

        for t in tabelas:
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {t} (
                id SERIAL PRIMARY KEY
            )
            """)

            cursor.execute(f"""
            ALTER TABLE {t}
            ADD COLUMN IF NOT EXISTS empresa_id TEXT
            """)

        # 🔥 AGORA SIM USA
        cursor.execute("""
        UPDATE usuarios
        SET empresa_id = usuario
        WHERE empresa_id IS NULL
        """)

        conn.commit()
        print("✅ BANCO OK + SAAS ATIVO")

    except Exception as e:
        print("❌ Erro ao criar banco:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            devolver_conexao(conn)


# ================= PAGAMENTO =================
def verificar_pagamento(usuario):
    return "pago"
