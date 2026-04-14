from flask import Blueprint, session, redirect
from banco import conectar, devolver_conexao
from layout import container
from datetime import datetime
import calendar
import json

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/painel")
def painel():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    try:
        # ===== DADOS =====
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM estoque")
        total_qtd = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transferencias")
        total_transferencias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE online=1")
        usuarios_online = cursor.fetchone()[0]

        # ===== CATEGORIAS (GRÁFICO) =====
        cursor.execute("""
        SELECT COALESCE(categoria, 'Sem categoria'), SUM(quantidade)
        FROM estoque
        GROUP BY categoria
        """)
        categorias = cursor.fetchall()

        nomes = [c[0] for c in categorias]
        valores = [c[1] for c in categorias]

        # ===== CALENDÁRIO =====
        now = datetime.now()
        ano = now.year
        mes = now.month
        nome_mes = calendar.month_name[mes].capitalize()

        cal = calendar.monthcalendar(ano, mes)
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]

        calendario_html = ""
        for d in dias_semana:
            calendario_html += f"<div class='head'>{d}</div>"

        for semana in cal:
            for dia in semana:
                if dia == 0:
                    calendario_html += "<div class='day vazio'></div>"
                else:
                    calendario_html += f"""
                    <div class="day">
                        <div class="numero">{dia}</div>
                        <div class="total">Mov: {dia}</div>
                    </div>
                    """

        html = f"""
        <div class="wrap">

            <div class="topo">
                <h2>📊 Dashboard</h2>
                <span>{nome_mes} de {ano}</span>
            </div>

            <div class="dashboard">

                <!-- ESQUERDA -->
                <div class="left">

                    <div class="box">
                        <h3>Resumo</h3>
                        <p>Produtos: {total_produtos}</p>
                        <p>Quantidade: {total_qtd}</p>
                        <p>Movimentações: {total_transferencias}</p>
                        <p>Online: {usuarios_online}</p>
                    </div>

                    <div class="box">
                        <h3>Distribuição</h3>
                        <canvas id="graficoPizza"></canvas>
                    </div>

                </div>

                <!-- DIREITA -->
                <div class="right">

                    <div class="box">
                        <h3>📅 Calendário</h3>
                        <div class="calendar">
                            {calendario_html}
                        </div>
                    </div>

                </div>

            </div>

        </div>

        <script>
        // 🔥 GRÁFICO PIZZA
        const ctx = document.getElementById('graficoPizza');

        new Chart(ctx, {{
            type: 'pie',
            data: {{
                labels: {json.dumps(nomes)},
                datasets: [{{
                    data: {json.dumps(valores)},
                    backgroundColor: [
                        '#3b82f6','#22c55e','#f59e0b','#ef4444',
                        '#8b5cf6','#06b6d4','#84cc16','#f97316'
                    ]
                }}]
            }}
        }});

        // 🔥 AUTO UPDATE
        setTimeout(() => {{
            location.reload();
        }}, 5000);
        </script>

        <style>

        .wrap {{
            max-width: 1400px;
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
            padding:10px;
            min-height:80px;
        }}

        .numero {{
            font-weight:bold;
        }}

        .total {{
            margin-top:5px;
            font-size:12px;
            color:#3b82f6;
        }}

        .vazio {{
            background:transparent;
            border:none;
        }}

        </style>
        """

        return container(html)

    finally:
        devolver_conexao(conn)
