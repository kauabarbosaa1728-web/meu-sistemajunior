def render_dashboard(
    total_produtos,
    total_qtd,
    total_transferencias,
    usuarios_online,
    nomes,
    valores,
    dias_labels,
    dias_valores,
    top_nomes,
    top_valores,
    baixo_nomes,
    baixo_valores,
    nome_mes,
    ano
):
    import json

    return f"""
    <div class="wrap">

        <div class="topo-dashboard">
            <div>
                <h2>📊 Dashboard Executivo • {nome_mes} {ano}
                    <span class="status-live">● AO VIVO</span>
                </h2>
                <p class="subtitulo">Dados atualizados em tempo real • Controle total do seu estoque</p>
            </div>
        </div>

        {"<div class='alerta-topo'>⚠️ Atenção: " + str(len(baixo_nomes)) + " produto(s) com estoque abaixo do mínimo</div>" if baixo_nomes else ""}

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
                <h1 style="color:#ffffff">{usuarios_online}</h1>
                <p>
                    <span class="status {'on' if usuarios_online > 0 else 'off'}"></span>
                    {'Online' if usuarios_online > 0 else 'Offline'}
                </p>
            </div>
        </div>

        <div class="grid">
            <div class="box"><h3>📊 Distribuição</h3><canvas id="pizza"></canvas></div>
            <div class="box"><h3>📈 Movimentações</h3><canvas id="linha"></canvas></div>
            <div class="box"><h3>🔥 Top Produtos</h3><canvas id="top"></canvas></div>
            <div class="box"><h3>⚠️ Baixo Estoque</h3><canvas id="baixo"></canvas></div>
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    const cores = ["#38bdf8","#60a5fa","#818cf8","#a78bfa","#22d3ee"];

    const baseOptions = {{
        responsive:true,
        maintainAspectRatio:false,
        animation:{{duration:1200}},
        plugins:{{legend:{{labels:{{color:"#ccc"}}}}}}
    }}

    new Chart(document.getElementById('pizza'), {{
        type:'doughnut',
        data:{{labels:{json.dumps(nomes)}, datasets:[{{data:{json.dumps(valores)}, backgroundColor:cores}}]}},
        options:{{...baseOptions, cutout:'65%'}}
    }});

    new Chart(document.getElementById('linha'), {{
        type:'line',
        data:{{
            labels:{json.dumps(dias_labels)},
            datasets:[{{
                label:"Movimentações",
                data:{json.dumps(dias_valores)},
                borderColor:"#38bdf8",
                tension:0.4
            }}]
        }},
        options:baseOptions
    }});

    new Chart(document.getElementById('top'), {{
        type:'bar',
        data:{{labels:{json.dumps(top_nomes)}, datasets:[{{data:{json.dumps(top_valores)}, backgroundColor:"#38bdf8"}}]}},
        options:{{...baseOptions, plugins:{{legend:{{display:false}}}}}}
    }});

    new Chart(document.getElementById('baixo'), {{
        type:'bar',
        data:{{labels:{json.dumps(baixo_nomes)}, datasets:[{{data:{json.dumps(baixo_valores)}, backgroundColor:"#ff4d4d"}}]}},
        options:{{...baseOptions, plugins:{{legend:{{display:false}}}}}}
    }});
    </script>

    <style>
    .wrap{{max-width:1300px;margin:auto}}

    .topo-dashboard{{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}}
    .subtitulo{{color:#64748b;font-size:13px}}
    .status-live{{color:#00ff9c;font-size:12px;margin-left:10px}}

    .cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:20px}}

    .card{{background:#020617;padding:20px;border-radius:15px;text-align:center}}
    .card h1{{font-size:42px;color:#38bdf8}}

    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}

    .box{{background:#020617;padding:15px;border-radius:15px;height:380px}}

    canvas{{width:100% !important;height:100% !important}}
    </style>
    """
