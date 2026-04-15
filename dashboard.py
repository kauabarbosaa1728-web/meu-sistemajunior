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
                    <canvas id="graficoPizza" class="grafico"></canvas>
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
                    ],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%',
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            color: '#ccc',
                            font: {{ size: 14 }}
                        }}
                    }}
                }},
                animation: {{
                    animateRotate: true,
                    duration: 1200
                }}
            }},
            plugins: [{{
                id: 'textoCentro',
                beforeDraw(chart) {{
                    const {{width, height, ctx}} = chart;
                    ctx.restore();

                    const total = chart.data.datasets[0].data.reduce((a,b)=>a+b,0);

                    ctx.font = 'bold 28px Arial';
                    ctx.fillStyle = '#3b82f6';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';

                    ctx.fillText(total, width / 2, height / 2);

                    ctx.font = '14px Arial';
                    ctx.fillStyle = '#aaa';
                    ctx.fillText('Total', width / 2, height / 2 + 25);

                    ctx.save();
                }}
            }}]
        }});
        </script>

        <style>

        .wrap {{
            max-width: 1200px;
            margin: auto;
        }}

        .topo {{
            display:flex;
            justify-content:space-between;
            margin-bottom:30px;
        }}

        .cards {{
            display:grid;
            grid-template-columns: repeat(4,1fr);
            gap:20px;
            margin-bottom:30px;
        }}

        .card {{
            background:#0b0b0b;
            border-radius:15px;
            padding:25px;
            text-align:center;
            box-shadow: 0 0 15px rgba(59,130,246,0.25);
        }}

        .card h1 {{
            font-size:40px;
        }}

        .dashboard {{
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:20px;
        }}

        .box {{
            background:#0b0b0b;
            border-radius:15px;
            padding:20px;
            text-align:center;
            box-shadow: 0 0 15px rgba(59,130,246,0.2);
        }}

        .grafico {{
            width: 280px !important;
            height: 280px !important;
            margin: auto;
        }}

        .calendar {{
            display:grid;
            grid-template-columns:repeat(7,1fr);
            gap:8px;
        }}

        .head {{
            background:#1a1a1a;
            border-radius:8px;
            color:#3b82f6;
            text-align:center;
            padding:8px;
        }}

        .day {{
            background:#111;
            border-radius:12px;
            padding:10px;
            min-height:90px;
        }}

        .numero {{
            font-weight:bold;
        }}

        .total {{
            color:#3b82f6;
        }}

        @media (max-width:768px){{
            .cards {{
                grid-template-columns:1fr 1fr;
            }}

            .dashboard {{
                grid-template-columns:1fr;
            }}
        }}

        </style>
        """

        return container(html)

    finally:
        devolver_conexao(conn)
