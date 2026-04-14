from werkzeug.security import generate_password_hash
from psycopg2 import pool

# ================= POOL DE CONEXÃO =================
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
except Exception as e:
    print("❌ ERRO AO CRIAR POOL:", e)
    db_pool = None


# ================= CONEXÃO =================
def conectar():
    try:
        if db_pool:
            return db_pool.getconn()
    except Exception as e:
        print("Erro ao conectar:", e)
    return None


def devolver_conexao(conn):
    try:
        if conn and db_pool:
            db_pool.putconn(conn)
    except Exception as e:
        print("Erro ao devolver conexão:", e)


# ================= LOGS =================
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
        if conn:
            conn.rollback()
    finally:
        if conn:
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

        # ================= USUARIOS =================
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

        # ================= PAGAMENTOS =================
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
        ADD COLUMN IF NOT EXISTS vencimento TIMESTAMP
        """)

        # ================= ESTOQUE =================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id SERIAL PRIMARY KEY,
            produto TEXT,
            quantidade INTEGER,
            categoria TEXT,
            valor DECIMAL(10,2)
        )
        """)

        # ================= TRANSFERENCIAS =================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transferencias (
            id SERIAL PRIMARY KEY,
            produto TEXT,
            quantidade INTEGER,
            origem TEXT,
            destino TEXT,
            usuario TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ================= LOGS =================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            usuario TEXT,
            acao TEXT,
            detalhes TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ================= FINANCEIRO =================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro (
            id SERIAL PRIMARY KEY,
            tipo VARCHAR(10),
            valor DECIMAL(10,2),
            descricao TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario TEXT
        )
        """)

        # ================= VENDAS =================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id SERIAL PRIMARY KEY,
            produto TEXT,
            quantidade INTEGER,
            valor_total DECIMAL(10,2),
            usuario TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("✅ BANCO OK")

    except Exception as e:
        print("❌ Erro ao criar banco:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            devolver_conexao(conn)


# ================= VERIFICAR PAGAMENTO =================
def verificar_pagamento(usuario):
    return "pago"
