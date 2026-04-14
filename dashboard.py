from flask import Blueprint, session, redirect
from banco import conectar, devolver_conexao
from layout import container
from permissoes import gerar_barras_3d
from datetime import datetime
import calendar

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

        # ===== CALENDÁRIO DINÂMICO =====
        now = datetime.now()
        ano = now.year
        mes = now.month

        cal = calendar.monthcalendar(ano, mes)

        calendario_html = ""
        for semana in cal:
            for dia in semana:
                if dia == 0:
                    calendario_html += "<div class='day vazio'></div>"
                else:
                    calendario_html += f"""
                    <div class="day">
                        <span>{dia}</span>
                        <div class="c aberto">Aberto: {dia % 5}</div>
                        <div class="c encerrado">Encerrado: {dia * 2}</div>
                        <div class="c execucao">Execução: {dia % 3}</div>
                        <div class="c pendente">Pendente: {dia % 2}</div>
                        <div class="c total">Total: {dia * 3}</div>
                    </div>
                    """

        # ===== HTML =====
        return container(f"""

        <div class="dashboard">

            <!-- ESQUERDA -->
            <div class="left">

                <div class="box">
                    <h3>📊 Resumo</h3>
                    <p>📦 Produtos: <b>{total_produtos}</b></p>
                    <p>🔢 Quantidade: <b>{total_qtd}</b></p>
                    <p>🔄 Movimentações: <b>{total_transferencias}</b></p>
                    <p>🟢 Online: <b>{usuarios_online}</b></p>
                </div>

                <div class="box">
                    <h3>📊 Categorias</h3>
                    {barras_categoria}
                </div>

                <div class="box">
                    <h3>📈 Transferências</h3>
                    {barras_transferencia}
                </div>

            </div>

            <!-- DIREITA -->
            <div class="right">

                <div class="box">
                    <h2>🏆 Top produtos</h2>
                    <table>
                        <tr>
                            <th>Produto</th>
                            <th>Quantidade</th>
                            <th>Categoria</th>
                        </tr>
                        {tabela_top}
                    </table>
                </div>

                <div class="box">
                    <h3>📅 Calendário - {mes}/{ano}</h3>

                    <div class="calendar">
                        {calendario_html}
                    </div>
                </div>

            </div>

        </div>

        <style>

        .dashboard {{
            display:flex;
            gap:20px;
        }}

        .left {{ width:30%; }}
        .right {{ width:70%; }}

        .box {{
            background:#0b0b0b;
            border:1px solid #2c2c2c;
            padding:15px;
            border-radius:10px;
            margin-bottom:15px;
        }}

        table {{
            width:100%;
            border-collapse:collapse;
        }}

        th {{
            background:#222;
        }}

        td, th {{
            padding:8px;
            border:1px solid #333;
        }}

        /* CALENDÁRIO */
        .calendar {{
            display:grid;
            grid-template-columns:repeat(7,1fr);
            gap:10px;
        }}

        .day {{
            background:#111;
            padding:8px;
            border:1px solid #333;
            font-size:12px;
        }}

        .day span {{
            font-weight:bold;
            display:block;
            margin-bottom:5px;
        }}

        .c {{ padding:2px; margin-bottom:2px; }}

        .aberto {{ background:#6b7280; }}
        .encerrado {{ background:#22c55e; }}
        .execucao {{ background:#f59e0b; }}
        .pendente {{ background:#ef4444; }}
        .total {{ background:#3b82f6; }}

        .vazio {{
            background:transparent;
            border:none;
        }}

        </style>

        """)

    except Exception as e:
        return container(f"<div style='color:red;'>Erro: {e}</div>")

    finally:
        devolver_conexao(conn)
