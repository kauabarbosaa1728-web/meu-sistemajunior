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

        # ===== CATEGORIAS =====
        cursor.execute("""
        SELECT COALESCE(categoria, 'Sem categoria'), SUM(quantidade)
        FROM estoque
        GROUP BY categoria
        """)
        categorias = cursor.fetchall()

        nomes = [c[0] for c in categorias]
        valores = [c[1] for c in categorias]

        # ===== DATA =====
        now = datetime.now()
        ano = now.year
        mes = now.month

        meses = [
            "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio",
            "Junho", "Julho", "Agosto", "Setembro", "Outubro",
            "Novembro", "Dezembro"
        ]

        nome_mes = meses[mes]

        # ===== CALENDÁRIO =====
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
                <h2>🚀 Dashboard</h2>
                <span>{nome_mes} de {ano}</span>
            </div>

            <!-- CARDS -->
            <div class="cards">

                <div class="card">
                    <span>📦 Produtos</span>
                    <h1>{total_produtos}</h1>
                </div>

                <div class="card">
                    <span>📊 Quantidade</span>
                    <h1>{total_qtd}</h1>
                </div>

                <div class="card">
                    <span>🔄 Movimentações</span>
                    <h1>{total_transferencias}</h1>
                </div>

                <div class="card">
                    <span>🟢 Online</span>
                    <h1>{usuarios_online}</h1>
                </div>

            </div>

            <div class="dashboard">

                <div class="box">
                    <h3>Distribuição</h3>
                    <canvas id="graficoPizza"></canvas>
                </div>

                <div class="box">
                    <h3>📅 Calendário</h3>
                    <div class="calendar">
                        {calendario_html}
                    </div>
                </div>

            </div>

        </div>

        <script>
        const ctx = document.getElementById('graficoPizza');

        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(nomes)},
                datasets: [{{
                    data: {json.dumps(valores)},
                    backgroundColor: [
                        '#3b82f6','#22c55e','#f59e0b','#ef4444',
                        '#8b5cf6','#06b6d4','#84cc16','#f97316'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
        </script>

        <style>

        .wrap {{
            max-width: 1000px;
            margin: auto;
        }}

        .topo {{
            display:flex;
            justify-content:space-between;
            margin-bottom:20px;
        }}

        /* CARDS */
        .cards {{
            display:grid;
            grid-template-columns: repeat(4,1fr);
            gap:15px;
            margin-bottom:20px;
        }}

        .card {{
            background:#0b0b0b;
            border:none;
            border-radius:12px;
            padding:15px;
            text-align:center;
            transition:0.3s;
            box-shadow: 0 0 10px rgba(59,130,246,0.25);
        }}

        .card:hover {{
            transform: scale(1.03);
            box-shadow: 0 0 20px rgba(59,130,246,0.5);
        }}

        .card h1 {{
            margin:10px 0 0 0;
            font-size:28px;
        }}

        /* DASHBOARD */
        .dashboard {{
            display:grid;
            grid-template-columns:1fr;
            gap:20px;
        }}

        .box {{
            background:#0b0b0b;
            border:none;
            border-radius:12px;
            padding:15px;
            box-shadow: 0 0 10px rgba(59,130,246,0.2);
        }}

        canvas {{
            width:100% !important;
            height:250px !important;
        }}

        /* CALENDÁRIO */
        .calendar {{
            display:grid;
            grid-template-columns:repeat(7,1fr);
            gap:6px;
        }}

        .head {{
            background:#1a1a1a;
            border:none;
            border-radius:8px;
            color:#3b82f6;
            text-align:center;
            padding:5px;
        }}

        .day {{
            background:#111;
            border:none;
            border-radius:10px;
            padding:8px;
            min-height:70px;
            box-shadow: inset 0 0 5px rgba(59,130,246,0.2);
        }}

        .numero {{
            font-weight:bold;
        }}

        .total {{
            font-size:12px;
            color:#3b82f6;
        }}

        .vazio {{
            border:none;
        }}

        /* MOBILE */
        @media (max-width:768px){{
            .cards {{
                grid-template-columns:1fr 1fr;
            }}
        }}

        </style>
        """

        return container(html)

    finally:
        devolver_conexao(conn)
