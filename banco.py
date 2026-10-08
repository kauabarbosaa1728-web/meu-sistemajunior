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

        # =====================================================
        # USUARIOS
        # =====================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            senha TEXT,
            cargo TEXT,
            online INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,

            -- ESTOQUE
            pode_estoque INTEGER DEFAULT 0,
            pode_transferencia INTEGER DEFAULT 0,
            pode_historico INTEGER DEFAULT 0,
            pode_editar_estoque INTEGER DEFAULT 0,
            pode_excluir_estoque INTEGER DEFAULT 0,
            pode_entrada_estoque INTEGER DEFAULT 0,
            pode_categorias INTEGER DEFAULT 0,
            pode_fornecedores INTEGER DEFAULT 0,
            pode_ncm INTEGER DEFAULT 0,
            pode_exportar_estoque INTEGER DEFAULT 0,
            pode_pdf_estoque INTEGER DEFAULT 0,

            -- SISTEMA
            pode_usuarios INTEGER DEFAULT 0,
            pode_logs INTEGER DEFAULT 0,

            -- FINANCEIRO
            pode_financeiro INTEGER DEFAULT 0,
            pode_entrada_financeiro INTEGER DEFAULT 0,
            pode_saida_financeiro INTEGER DEFAULT 0,
            pode_resumo_financeiro INTEGER DEFAULT 0,
            pode_relatorio_financeiro INTEGER DEFAULT 0,

            -- VENDAS
            pode_vendas INTEGER DEFAULT 0,
            pode_historico_vendas INTEGER DEFAULT 0,

            -- RELATORIOS
            pode_relatorios INTEGER DEFAULT 0,
            pode_relatorio_geral INTEGER DEFAULT 0,
            pode_relatorio_estoque INTEGER DEFAULT 0,
            pode_relatorio_veiculos INTEGER DEFAULT 0,
            pode_relatorio_problemas INTEGER DEFAULT 0,

            -- VEICULOS
            pode_veiculos INTEGER DEFAULT 0,
            pode_manutencoes INTEGER DEFAULT 0,
            pode_dashboard INTEGER DEFAULT 0,
            pode_rotas INTEGER DEFAULT 0,

            -- PROBLEMAS
            pode_problemas INTEGER DEFAULT 0,
            pode_ocorrencias INTEGER DEFAULT 0,
            pode_resolver_problemas INTEGER DEFAULT 0,
            pode_excluir_problemas INTEGER DEFAULT 0,
            pode_pdf_problemas INTEGER DEFAULT 0,

            -- OUTROS
            pode_ia INTEGER DEFAULT 0,
            pode_configuracoes INTEGER DEFAULT 0,

            email TEXT,
            plano TEXT DEFAULT 'basico',
            nome_empresa TEXT
        )
        """)

        # ================= EMPRESA =================

        cursor.execute("""
        ALTER TABLE usuarios
        ADD COLUMN IF NOT EXISTS empresa_id TEXT
        """)

        # =====================================================
        # GARANTIR PERMISSOES EM BANCOS EXISTENTES
        # =====================================================

        permissoes = [

            # ESTOQUE
            "pode_estoque",
            "pode_transferencia",
            "pode_historico",
            "pode_editar_estoque",
            "pode_excluir_estoque",
            "pode_entrada_estoque",
            "pode_categorias",
            "pode_fornecedores",
            "pode_ncm",
            "pode_exportar_estoque",
            "pode_pdf_estoque",

            # SISTEMA
            "pode_usuarios",
            "pode_logs",

            # FINANCEIRO
            "pode_financeiro",
            "pode_entrada_financeiro",
            "pode_saida_financeiro",
            "pode_resumo_financeiro",
            "pode_relatorio_financeiro",

            # VENDAS
            "pode_vendas",
            "pode_historico_vendas",

            # RELATORIOS
            "pode_relatorios",
            "pode_relatorio_geral",
            "pode_relatorio_estoque",
            "pode_relatorio_veiculos",
            "pode_relatorio_problemas",

            # VEICULOS
            "pode_veiculos",
            "pode_manutencoes",
            "pode_dashboard",
            "pode_rotas",

            # PROBLEMAS
            "pode_problemas",
            "pode_ocorrencias",
            "pode_resolver_problemas",
            "pode_excluir_problemas",
            "pode_pdf_problemas",

            # OUTROS
            "pode_ia",
            "pode_configuracoes"
        ]

        for permissao in permissoes:
            cursor.execute(f"""
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS {permissao} INTEGER DEFAULT 0
            """)

        # =====================================================
        # PAGAMENTOS
        # =====================================================

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

        # =====================================================
        # TABELAS BASE
        # =====================================================

        tabelas = [
            "estoque",
            "transferencias",
            "logs",
            "financeiro",
            "vendas"
        ]

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

        # =====================================================
        # VEICULOS
        # =====================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id SERIAL PRIMARY KEY,
            placa TEXT NOT NULL,
            empresa_id TEXT
        )
        """)

        cursor.execute("""
        ALTER TABLE veiculos
        ADD COLUMN IF NOT EXISTS motorista TEXT
        """)

        cursor.execute("""
        ALTER TABLE veiculos
        ADD COLUMN IF NOT EXISTS nome TEXT
        """)

        cursor.execute("""
        ALTER TABLE veiculos
        ADD COLUMN IF NOT EXISTS equipe TEXT
        """)

        # =====================================================
        # MANUTENCOES
        # =====================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS manutencoes (
            id SERIAL PRIMARY KEY,
            data DATE,
            valor NUMERIC,
            veiculo_id INTEGER,
            oficina TEXT,
            descricao TEXT,
            quantidade INTEGER,
            validade DATE,
            empresa_id TEXT
        )
        """)

        cursor.execute("""
        ALTER TABLE manutencoes
        ADD COLUMN IF NOT EXISTS empresa_id TEXT
        """)

        # =====================================================
        # PROBLEMAS
        # =====================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS problemas (
            id SERIAL PRIMARY KEY,
            tipo TEXT,
            descricao TEXT,
            foto TEXT,
            data TIMESTAMP,
            empresa_id TEXT
        )
        """)

        cursor.execute("""
        ALTER TABLE problemas
        ADD COLUMN IF NOT EXISTS usuario TEXT
        """)

        cursor.execute("""
        ALTER TABLE problemas
        ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'aberto'
        """)

        cursor.execute("""
        ALTER TABLE problemas
        ADD COLUMN IF NOT EXISTS empresa_id TEXT
        """)

        # =====================================================
        # EMPRESA DOS USUARIOS ANTIGOS
        # =====================================================

        cursor.execute("""
        UPDATE usuarios
        SET empresa_id = usuario
        WHERE empresa_id IS NULL
        """)

        # =====================================================
        # FINALIZAR
        # =====================================================

        conn.commit()

        print("✅ BANCO COMPLETO ATUALIZADO")
        print("✅ NOVAS PERMISSOES CRIADAS")

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
