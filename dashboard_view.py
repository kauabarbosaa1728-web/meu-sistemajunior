import json
import calendar
from datetime import datetime

def render_dashboard(
    total_produtos,
    total_qtd,
    total_transferencias,
    usuarios_online,
    nomes,
    valores,
    top_nomes,
    top_valores,
    dias_labels,
    dias_valores,
    baixo_nomes,
    baixo_valores,
    calendario
):
    now = datetime.now()

    nome_mes = [
        "", "Janeiro","Fevereiro","Março","Abril","Maio",
        "Junho","Julho","Agosto","Setembro","Outubro",
        "Novembro","Dezembro"
    ][now.month]

    mes = now.month
    ano = now.year
    cal = calendar.monthcalendar(ano, mes)

    # 🔥 CALENDÁRIO
    html_calendario = f"""
    <div class="box calendario-box">

        <div class="topo-cal">
            <span>📅 Calendário • {nome_mes} {ano}</span>
        </div>

        <div class="cal-grid">
    """

    dias_semana = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]

    for d in dias_semana:
        html_calendario += f"<div class='dia-semana'>{d}</div>"

    for semana in cal:
        for dia in semana:
            if dia == 0:
                html_calendario += "<div class='dia vazio'></div>"
            else:
                data_str = f"{ano}-{mes:02d}-{dia:02d}"
                info = calendario.get(data_str, {})

                entrada = info.get("entrada", 0)
                saida = info.get("saida", 0)
                transf = info.get("transf", 0)
                total = info.get("total", 0)

                hoje_classe = "hoje" if dia == now.day else ""

                html_calendario += f"""
                <div class="dia {hoje_classe}">
                    <div class="num">{dia}</div>

                    <div class="linha verde">Entrada: {entrada}</div>
                    <div class="linha vermelho">Saída: {saida}</div>
                    <div class="linha azul">Transf: {transf}</div>

                    <div class="total">Total: {total}</div>
                </div>
                """

    html_calendario += "</div></div>"

    html = f"""
    <style>

    .calendario-box {{
        margin-top:20px;
    }}

    .topo-cal {{
        color:#94a3b8;
        margin-bottom:10px;
        font-weight:bold;
    }}

    .cal-grid {{
        display:grid;
        grid-template-columns: repeat(7, 1fr);
        gap:8px;
    }}

    .dia-semana {{
        text-align:center;
        font-size:12px;
        color:#64748b;
    }}

    .dia {{
        background: linear-gradient(145deg, #020617, #0f172a);
        border:1px solid #1e293b;
        border-radius:12px;
        padding:10px;
        min-height:110px;
        position:relative;
        transition:0.2s;
    }}

    .dia:hover {{
        transform:scale(1.05);
        box-shadow:0 0 15px rgba(59,130,246,0.3);
    }}

    .dia.hoje {{
        border:2px solid #3b82f6;
        box-shadow:0 0 10px #3b82f6;
    }}

    .num {{
        font-weight:bold;
        color:#fff;
        margin-bottom:5px;
    }}

    .linha {{
        font-size:11px;
        margin:2px 0;
    }}

    .verde {{ color:#22c55e; }}
    .vermelho {{ color:#ef4444; }}
    .azul {{ color:#38bdf8; }}

    .total {{
        position:absolute;
        bottom:6px;
        right:10px;
        font-size:12px;
        color:#fff;
        font-weight:bold;
    }}

    .vazio {{
        background:transparent;
        border:none;
    }}

    /* 🔥 GRID PROFISSIONAL */
    .grid {{
        display: grid;
        grid-template-columns: 2fr 1fr;
        grid-template-rows: 300px 300px;
        gap: 20px;
        margin-top: 25px;
    }}

    .grid .box:nth-child(1) {{
        grid-row: span 2;
    }}

    .box {{
        background: linear-gradient(145deg, #020617, #0f172a);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }}

    canvas {{
        width: 100% !important;
        height: 100% !important;
    }}

    </style>

    <div class="wrap">

        <div class="topo-dashboard">
            <div>
                <h2>📊 Dashboard Executivo • {nome_mes} {now.year}</h2>
                <p class="subtitulo">Dados atualizados em tempo real • Controle total do seu estoque</p>
            </div>

            <form method="get" class="filtro-data">
                <div class="campo">
                    <label>De</label>
                    <input type="date" name="inicio">
                </div>

                <div class="campo">
                    <label>Até</label>
                    <input type="date" name="fim">
                </div>

                <button>Filtrar</button>
            </form>
        </div>

        {"<div class='alerta-topo'>⚠️ Atenção: " + str(len(baixo_nomes)) + " produto(s) com estoque baixo</div>" if baixo_nomes else ""}

        <div class="cards">
            <div class="card">
                <h1 class="azul">{total_produtos}</h1>
                <p>Total Produtos</p>
            </div>

            <div class="card">
                <h1 class="azul">{total_qtd}</h1>
                <p>Quantidade</p>
            </div>

            <div class="card">
                <h1 class="azul">{total_transferencias}</h1>
                <p>Movimentações</p>
            </div>

            <div class="card">
                <h1 style="color:#fff">{usuarios_online}</h1>
                <p>
                    <span class="status {'on' if usuarios_online > 0 else 'off'}"></span>
                    {'Online' if usuarios_online > 0 else 'Offline'}
                </p>
            </div>
        </div>

        {html_calendario}

        <div class="grid">
            <div class="box"><canvas id="linha"></canvas></div>
            <div class="box"><canvas id="pizza"></canvas></div>
            <div class="box"><canvas id="top"></canvas></div>
            <div class="box"><canvas id="baixo"></canvas></div>
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>

    const cores = ["#38bdf8","#60a5fa","#818cf8","#a78bfa","#22d3ee"]

    const configPadrao = {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{ labels: {{ color: "#cbd5e1" }} }}
        }},
        scales: {{
            x: {{
                ticks: {{ color: "#94a3b8" }},
                grid: {{ color: "rgba(255,255,255,0.05)" }}
            }},
            y: {{
                ticks: {{ color: "#94a3b8" }},
                grid: {{ color: "rgba(255,255,255,0.05)" }}
            }}
        }}
    }}

    new Chart(document.getElementById('pizza'), {{
        type:'doughnut',
        data:{{
            labels:{json.dumps(nomes)},
            datasets:[{{
                data:{json.dumps(valores)},
                backgroundColor: cores,
                borderWidth:0
            }}]
        }},
        options:{{
            responsive:true,
            maintainAspectRatio:false,
            cutout:'70%',
            plugins:{{
                legend:{{ position:'bottom', labels:{{ color:'#cbd5e1' }} }}
            }}
        }}
    }});

    new Chart(document.getElementById('linha'), {{
        type:'line',
        data:{{
            labels:{json.dumps(dias_labels)},
            datasets:[{{
                data:{json.dumps(dias_valores)},
                borderColor:"#38bdf8",
                backgroundColor:"rgba(56,189,248,0.2)",
                fill:true,
                borderWidth:3,
                tension:0.4,
                pointRadius:4
            }}]
        }},
        options: configPadrao
    }});

    new Chart(document.getElementById('top'), {{
        type:'bar',
        data:{{
            labels:{json.dumps(top_nomes)},
            datasets:[{{
                data:{json.dumps(top_valores)},
                backgroundColor:"#3b82f6",
                borderRadius:8
            }}]
        }},
        options: configPadrao
    }});

    new Chart(document.getElementById('baixo'), {{
        type:'bar',
        data:{{
            labels:{json.dumps(baixo_nomes)},
            datasets:[{{
                data:{json.dumps(baixo_valores)},
                backgroundColor:"#ef4444",
                borderRadius:8
            }}]
        }},
        options: configPadrao
    }});

    </script>
    """

    return html
