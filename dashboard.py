from flask import Blueprint, session, redirect
from banco import conectar, devolver_conexao
from layout import container
from permissoes import gerar_barras_3d

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/painel")
def painel():
    if "user" not in session:
        return redirect("/")

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        # ===== DADOS =====
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM estoque")
        total_qtd = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transferencias")
        total_transferencias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE online=1")
        usuarios_online = cursor.fetchone()[0]

        # ===== GRÁFICOS =====
        cursor.execute("""
        SELECT COALESCE(categoria, 'Sem categoria'), COALESCE(SUM(quantidade), 0)
        FROM estoque
        GROUP BY categoria
        ORDER BY SUM(quantidade) DESC
        LIMIT 8
        """)
        categorias = cursor.fetchall()

        cursor.execute("""
        SELECT COALESCE(produto, 'Sem nome'), COALESCE(SUM(quantidade), 0)
        FROM transferencias
        GROUP BY produto
        ORDER BY SUM(quantidade) DESC
        LIMIT 8
        """)
        transferencias_produto = cursor.fetchall()

        barras_categoria = gerar_barras_3d(categorias, 220, "categoria")
        barras_transferencia = gerar_barras_3d(transferencias_produto, 220, "transferencia")

        # ===== TOP PRODUTOS =====
        cursor.execute("""
        SELECT produto, quantidade, categoria
        FROM estoque
        ORDER BY quantidade DESC
        LIMIT 5
        """)
        top_produtos = cursor.fetchall()

        tabela_top = ""
        for produto, quantidade, categoria in top_produtos:
            tabela_top += f"""
            <tr>
                <td>{produto}</td>
                <td>{quantidade}</td>
                <td>{categoria}</td>
            </tr>
            """

        if not tabela_top:
            tabela_top = "<tr><td colspan='3'>Sem dados</td></tr>"

        # ===== HTML =====
        return container(f"""

        <div style="background:#111;padding:20px;border-radius:10px;margin-bottom:20px;">
            <h2 style="color:#fff;">🖥️ PAINEL DO SISTEMA</h2>
            <p style="color:#aaa;">Bem-vindo, <b>{session["user"]}</b> | Cargo: <b>{session.get("cargo","")}</b></p>
        </div>

        <!-- CARDS -->
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:25px;">

            <div style="background:#1f1f1f;padding:20px;border-radius:10px;text-align:center;">
                <h3>📦 Produtos</h3>
                <h1>{total_produtos}</h1>
            </div>

            <div style="background:#1f1f1f;padding:20px;border-radius:10px;text-align:center;">
                <h3>🔢 Quantidade</h3>
                <h1>{total_qtd}</h1>
            </div>

            <div style="background:#1f1f1f;padding:20px;border-radius:10px;text-align:center;">
                <h3>🔄 Movimentações</h3>
                <h1>{total_transferencias}</h1>
            </div>

            <div style="background:#1f1f1f;padding:20px;border-radius:10px;text-align:center;">
                <h3>🟢 Online</h3>
                <h1>{usuarios_online}</h1>
            </div>

        </div>

        <!-- GRÁFICOS -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:25px;">

            <div style="background:#1f1f1f;padding:20px;border-radius:10px;">
                <h3>📊 Produtos por categoria</h3>
                {barras_categoria}
            </div>

            <div style="background:#1f1f1f;padding:20px;border-radius:10px;">
                <h3>📈 Transferências</h3>
                {barras_transferencia}
            </div>

        </div>

        <!-- TABELA -->
        <div style="background:#1f1f1f;padding:20px;border-radius:10px;">
            <h2>🏆 Top produtos</h2>
            <table style="width:100%;border-collapse:collapse;">
                <tr style="background:#333;">
                    <th>Produto</th>
                    <th>Quantidade</th>
                    <th>Categoria</th>
                </tr>
                {tabela_top}
            </table>
        </div>

        """)

    except Exception as e:
        return container(f"<div style='color:red;'>Erro: {e}</div>")

    finally:
        devolver_conexao(conn)
