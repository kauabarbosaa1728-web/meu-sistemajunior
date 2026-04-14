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
    FROM estoque GROUP BY categoria
    ORDER BY SUM(quantidade) DESC LIMIT 8
    """)
    categorias = cursor.fetchall()

    barras_categoria = gerar_barras_3d(categorias, 180, "categoria")

    # ===== CALENDÁRIO =====
    now = datetime.now()
    ano = now.year
    mes = now.month
    nome_mes = calendar.month_name[mes].capitalize()

    cal = calendar.monthcalendar(ano, mes)

    dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]

    calendario_html = ""

    # Cabeçalho dias
    for dia_nome in dias_semana:
        calendario_html += f"<div class='head'>{dia_nome}</div>"

    # Dias
    for semana in cal:
        for dia in semana:
            if dia == 0:
                calendario_html += "<div class='day vazio'></div>"
            else:
                calendario_html += f"""
                <div class="day">
                    <div class="numero">{dia}</div>
                    <div class="c aberto">A: {dia % 5}</div>
                    <div class="c encerrado">E: {dia * 2}</div>
                    <div class="c execucao">Ex: {dia % 3}</div>
                    <div class="c pendente">P: {dia % 2}</div>
                    <div class="c total">T: {dia * 3}</div>
                </div>
                """

    html = f"""

    <div class="wrap">

        <div class="topo">
            <h2>🖥️ Painel do Sistema</h2>
            <span>{nome_mes} de {ano}</span>
        </div>

        <div class="dashboard">

            <!-- ESQUERDA -->
            <div class="left">

                <div class="box destaque">
                    <h3>Resumo Geral</h3>
                    <p>📦 Produtos: <b>{total_produtos}</b></p>
                    <p>🔢 Quantidade: <b>{total_qtd}</b></p>
                    <p>🔄 Movimentações: <b>{total_transferencias}</b></p>
                    <p>🟢 Online: <b>{usuarios_online}</b></p>
                </div>

                <div class="box">
                    <h3>Categorias</h3>
                    {barras_categoria}
                </div>

            </div>

            <!-- DIREITA -->
            <div class="right">

                <div class="box calendario-box">
                    <h3>📅 Calendário - {nome_mes}/{ano}</h3>

                    <div class="calendar">
                        {calendario_html}
                    </div>

                </div>

            </div>

        </div>

    </div>

    <style>

    .wrap {{
        max-width: 1500px;
        margin: auto;
    }}

    .topo {{
        display:flex;
        justify-content:space-between;
        margin-bottom:20px;
    }}

    .dashboard {{
        display:flex;
        gap:20px;
    }}

    .left {{ width:25%; }}
    .right {{ width:75%; }}

    .box {{
        background:#0b0b0b;
        border:1px solid #2c2c2c;
        padding:15px;
        border-radius:10px;
        margin-bottom:20px;
    }}

    .destaque {{
        border-left:4px solid #3b82f6;
    }}

    /* CALENDÁRIO */
    .calendar {{
        display:grid;
        grid-template-columns:repeat(7,1fr);
        gap:6px;
    }}

    .head {{
        text-align:center;
        font-weight:bold;
        padding:5px;
        background:#1a1a1a;
    }}

    .day {{
        background:#111;
        border:1px solid #333;
        padding:5px;
        min-height:90px;
        font-size:11px;
    }}

    .numero {{
        font-weight:bold;
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
    """

    devolver_conexao(conn)
    return container(html)
