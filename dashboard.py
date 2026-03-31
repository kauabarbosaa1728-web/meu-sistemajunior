from flask import Blueprint, session, redirect
from banco import conectar, devolver_conexao
from layout import container, gerar_barras_3d

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/painel")
def painel():
    if "user" not in session:
        return redirect("/")

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM estoque")
        total_qtd = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transferencias")
        total_transferencias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE online=1")
        usuarios_online = cursor.fetchone()[0]

        cursor.execute("""
        SELECT COALESCE(categoria, 'Sem categoria') AS categoria, COALESCE(SUM(quantidade), 0) AS total
        FROM estoque
        GROUP BY categoria
        ORDER BY total DESC, categoria ASC
        LIMIT 8
        """)
        categorias = cursor.fetchall()

        cursor.execute("""
        SELECT COALESCE(produto, 'Sem nome') AS produto, COALESCE(SUM(quantidade), 0) AS total
        FROM transferencias
        GROUP BY produto
        ORDER BY total DESC, produto ASC
        LIMIT 8
        """)
        transferencias_produto = cursor.fetchall()

        cursor.execute("""
        SELECT produto, quantidade, categoria
        FROM estoque
        ORDER BY quantidade DESC, produto ASC
        LIMIT 5
        """)
        top_produtos = cursor.fetchall()

        barras_categoria = gerar_barras_3d(categorias, 220, "categoria")
        barras_transferencia = gerar_barras_3d(transferencias_produto, 220, "transferencia")

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
            tabela_top = """
            <tr>
                <td colspan="3">Sem produtos cadastrados.</td>
            </tr>
            """

        return container(f"""
        <div class="card">
            <h2>🖥️ PAINEL DO SISTEMA</h2>
            <p>Bem-vindo, <b>{session["user"]}</b> | Cargo: <b>{session.get("cargo", "")}</b></p>
            <p>Este sistema permite controlar o estoque, registrar transferências, acompanhar o histórico, gerenciar usuários e auditar ações com logs.</p>
        </div>

        <div class="cards">
            <div class="mini-card">
                <h3>📦 Produtos cadastrados</h3>
                <p style="font-size:32px;">{total_produtos}</p>
            </div>
            <div class="mini-card">
                <h3>🔢 Quantidade total</h3>
                <p style="font-size:32px;">{total_qtd}</p>
            </div>
            <div class="mini-card">
                <h3>🔄 Transferências</h3>
                <p style="font-size:32px;">{total_transferencias}</p>
            </div>
            <div class="mini-card">
                <h3>🟢 Usuários online</h3>
                <p style="font-size:32px;">{usuarios_online}</p>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="chart-3d-card">
                <div class="chart-title">📊 Produtos por categoria</div>
                <div class="chart-3d-area">
                    {barras_categoria}
                </div>
            </div>

            <div class="chart-3d-card">
                <div class="chart-title">📈 Transferências por produto</div>
                <div class="chart-3d-area">
                    {barras_transferencia}
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🏆 Top 5 produtos com maior quantidade</h2>
            <table class="ranking-table">
                <tr>
                    <th>Produto</th>
                    <th>Quantidade</th>
                    <th>Categoria</th>
                </tr>
                {tabela_top}
            </table>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro no painel: {e}</h2></div>')
    finally:
        devolver_conexao(conn)
