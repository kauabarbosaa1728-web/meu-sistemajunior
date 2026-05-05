from banco import conectar, devolver_conexao


def buscar_estoque_completo():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, produto, quantidade, categoria, valor
            FROM estoque
            ORDER BY id DESC
        """)
        return cursor.fetchall()
    finally:
        devolver_conexao(conn)


def buscar_estoque_exportacao():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT produto, quantidade, categoria, valor
            FROM estoque
            ORDER BY produto ASC
        """)
        return cursor.fetchall()
    finally:
        devolver_conexao(conn)


def inserir_produto(produto, qtd, categoria, valor):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO estoque (produto, quantidade, categoria, valor)
            VALUES (%s, %s, %s, %s)
        """, (produto, qtd, categoria, valor))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        devolver_conexao(conn)


def buscar_produto_por_id(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT produto, quantidade, categoria, valor
            FROM estoque
            WHERE id=%s
        """, (id,))
        return cursor.fetchone()
    finally:
        devolver_conexao(conn)


def atualizar_produto(id, produto, qtd, categoria, valor):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE estoque 
            SET produto=%s, quantidade=%s, categoria=%s, valor=%s
            WHERE id=%s
        """, (produto, qtd, categoria, valor, id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        devolver_conexao(conn)


def excluir_produto(id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM estoque WHERE id=%s", (id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        devolver_conexao(conn)


def buscar_estoque_baixo():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT produto, quantidade
            FROM estoque
            WHERE quantidade <= 10
            ORDER BY quantidade ASC
            LIMIT 5
        """)
        return cursor.fetchall()
    finally:
        devolver_conexao(conn)


def listar_produtos_transferencia():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT produto FROM estoque")
        return [p[0] for p in cursor.fetchall()]
    finally:
        devolver_conexao(conn)


def listar_usuarios_transferencia():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT usuario FROM usuarios")
        return [u[0] for u in cursor.fetchall()]
    except Exception:
        return []
    finally:
        devolver_conexao(conn)


def buscar_quantidade_produto(produto):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
        return cursor.fetchone()
    finally:
        devolver_conexao(conn)


def fazer_transferencia(produto, qtd, destino, usuario):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
        dado = cursor.fetchone()

        if not dado or dado[0] < qtd:
            return False, "❌ Estoque insuficiente"

        cursor.execute("""
            UPDATE estoque 
            SET quantidade=%s 
            WHERE produto=%s
        """, (dado[0] - qtd, produto))

        cursor.execute("""
            INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
            VALUES (%s, %s, %s, %s, %s)
        """, (produto, qtd, "estoque", destino or "saida", usuario))

        conn.commit()
        return True, "✅ Transferência realizada"

    except Exception as e:
        conn.rollback()
        return False, f"❌ Erro: {e}"

    finally:
        devolver_conexao(conn)


def buscar_historico_transferencias():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT produto, quantidade, destino, usuario, data
            FROM transferencias 
            ORDER BY id DESC 
            LIMIT 10
        """)
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        devolver_conexao(conn)


def buscar_logs(busca):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT usuario, acao, detalhes, data
            FROM logs
            WHERE usuario ILIKE %s OR acao ILIKE %s OR detalhes ILIKE %s
            ORDER BY data DESC
            LIMIT 100
        """, (f"%{busca}%", f"%{busca}%", f"%{busca}%"))
        return cursor.fetchall()
    finally:
        devolver_conexao(conn)


def criar_tabela_entradas():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entradas (
                id SERIAL PRIMARY KEY,
                produto TEXT,
                quantidade INT,
                categoria TEXT,
                fornecedor TEXT,
                valor NUMERIC,
                usuario TEXT,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        devolver_conexao(conn)


def inserir_entrada(produto, qtd, categoria, fornecedor, valor, usuario):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO estoque (produto, quantidade, categoria, valor)
            VALUES (%s, %s, %s, %s)
        """, (produto, qtd, categoria, valor))

        cursor.execute("""
            INSERT INTO entradas (produto, quantidade, categoria, fornecedor, valor, usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (produto, qtd, categoria, fornecedor, valor, usuario))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        devolver_conexao(conn)


def buscar_historico_entradas():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT produto, quantidade, fornecedor, valor, usuario, data
            FROM entradas
            ORDER BY id DESC LIMIT 10
        """)
        return cursor.fetchall()
    finally:
        devolver_conexao(conn)
