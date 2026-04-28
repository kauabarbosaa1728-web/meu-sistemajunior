import json
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
    baixo_valores
):
    now = datetime.now()

    nome_mes = [
        "", "Janeiro","Fevereiro","Março","Abril","Maio",
        "Junho","Julho","Agosto","Setembro","Outubro",
        "Novembro","Dezembro"
    ][now.month]

    html = f"""
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

        <div class="grid">
            <div class="box"><canvas id="pizza"></canvas></div>
            <div class="box"><canvas id="linha"></canvas></div>
            <div class="box"><canvas id="top"></canvas></div>
            <div class="box"><canvas id="baixo"></canvas></div>
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    const cores = ["#38bdf8","#60a5fa","#818cf8","#a78bfa","#22d3ee"]

    new Chart(document.getElementById('pizza'), {{
        type:'doughnut',
        data:{{labels:{json.dumps(nomes)}, datasets:[{{data:{json.dumps(valores)}, backgroundColor:cores}}]}}
    }});

    new Chart(document.getElementById('linha'), {{
        type:'line',
        data:{{
            labels:{json.dumps(dias_labels)},
            datasets:[{{data:{json.dumps(dias_valores)}, borderColor:"#38bdf8"}}]
        }}
    }});

    new Chart(document.getElementById('top'), {{
        type:'bar',
        data:{{labels:{json.dumps(top_nomes)}, datasets:[{{data:{json.dumps(top_valores)}}}]}}
    }});

    new Chart(document.getElementById('baixo'), {{
        type:'bar',
        data:{{labels:{json.dumps(baixo_nomes)}, datasets:[{{data:{json.dumps(baixo_valores)}}}]}}
    }});
    </script>
    """

    return html
