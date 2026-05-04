from flask import redirect, session
from banco import conectar, devolver_conexao
from layout import container
from . import financeiro_bp
import json


@financeiro_bp.route("/resumo-financeiro")
def resumo_financeiro():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada' AND usuario=%s",
        (session["user"],)
    )
    entradas = float(cursor.fetchone()[0])

    cursor.execute(
        "SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida' AND usuario=%s",
        (session["user"],)
    )
    saidas = float(cursor.fetchone()[0])

    devolver_conexao(conn)

    saldo = entradas - saidas

    labels_json = json.dumps(["Entradas", "Saídas", "Saldo"])
    valores_json = json.dumps([entradas, saidas, saldo])

    return container(f"""
    <div class="wrap">

        <h2>📊 Resumo Geral</h2>

        <div class="cards">

            <div class="card green">
                <h3>Entradas</h3>
                <p>R$ {entradas:.2f}</p>
            </div>

            <div class="card red">
                <h3>Saídas</h3>
                <p>R$ {saidas:.2f}</p>
            </div>

            <div class="card blue">
                <h3>Saldo</h3>
                <p>R$ {saldo:.2f}</p>
            </div>

        </div>

        <div class="box">
            <h3>📈 Visão Geral</h3>
            <canvas id="graficoResumo"></canvas>
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    new Chart(document.getElementById('graficoResumo'), {{
        type: 'bar',
        data: {{
            labels: {labels_json},
            datasets: [{{
                data: {valores_json},
                backgroundColor: ["#22c55e", "#ef4444", "#3b82f6"],
                borderRadius: 12
            }}]
        }},
        options: {{
            responsive:true,
            maintainAspectRatio:false,
            plugins: {{
                legend: {{display:false}}
            }}
        }}
    }});
    </script>

    <style>
    .wrap {{
        max-width:1300px;
        margin:auto;
    }}

    .cards {{
        display:flex;
        gap:15px;
        margin-bottom:20px;
    }}

    .card {{
        flex:1;
        padding:22px;
        border-radius:14px;
        background:#020617;
        border:1px solid rgba(56,189,248,0.2);
        text-align:center;
        box-shadow:0 10px 25px rgba(0,0,0,0.20);
    }}

    .green {{ border-left:4px solid #22c55e; }}
    .red {{ border-left:4px solid #ef4444; }}
    .blue {{ border-left:4px solid #3b82f6; }}

    .card p {{
        font-size:26px;
        font-weight:bold;
        margin:10px 0 0 0;
    }}

    .box {{
        background:#020617;
        border:1px solid #1e293b;
        padding:20px;
        border-radius:14px;
        margin-bottom:20px;
        box-shadow:0 10px 25px rgba(0,0,0,0.18);
    }}

    canvas {{
        width:100% !important;
        height:300px !important;
    }}

    @media(max-width: 850px) {{
        .cards {{
            display:block;
        }}

        .card {{
            margin-bottom:15px;
        }}
    }}
    </style>
    """)
