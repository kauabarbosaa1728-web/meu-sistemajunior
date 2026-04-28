from flask import Blueprint, session, redirect, request
from banco import conectar, devolver_conexao
from layout import container
from datetime import datetime
import json

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/painel")
def painel():
    if "user" not in session:
        return redirect("/")

    # 🔥 FILTRO DE DATA
    data_inicio = request.args.get("inicio")
    data_fim = request.args.get("fim")

    conn = conectar()
    cursor = conn.cursor()

    try:
        filtro = ""
        valores_filtro = ()

        if data_inicio and data_fim:
            filtro = "WHERE DATE(data) BETWEEN %s AND %s"
            valores_filtro = (data_inicio, data_fim)

        # ===== DADOS =====
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM estoque")
        total_qtd = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM transferencias {filtro}", valores_filtro)
        total_transferencias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE online=1")
        usuarios_online = cursor.fetchone()[0]

        # ===== DISTRIBUIÇÃO =====
        cursor.execute("""
        SELECT COALESCE(categoria, 'Sem categoria'), SUM(quantidade)
        FROM estoque
        GROUP BY categoria
        """)
        categorias = cursor.fetchall()

        nomes = [c[0] if c[0] else "Sem categoria" for c in categorias]
        valores = [c[1] if c[1] else 0 for c in categorias]

        # ===== TOP PRODUTOS =====
        cursor.execute(f"""
        SELECT COALESCE(produto, 'Sem nome'), SUM(quantidade)
        FROM transferencias
        {filtro}
        GROUP BY produto
        ORDER BY SUM(quantidade) DESC
        LIMIT 5
        """, valores_filtro)
        top = cursor.fetchall()

        top_nomes = [t[0] if t[0] else "Sem nome" for t in top]
        top_valores = [t[1] if t[1] else 0 for t in top]

        # ===== MOVIMENTAÇÃO =====
        cursor.execute(f"""
        SELECT DATE(data), COUNT(*)
        FROM transferencias
        {filtro}
        GROUP BY DATE(data)
        ORDER BY DATE(data)
        """, valores_filtro)
        dias = cursor.fetchall()

        dias_labels = [str(d[0]) for d in dias]
        dias_valores = [d[1] if d[1] else 0 for d in dias]

        # ===== BAIXO ESTOQUE =====
        cursor.execute("""
        SELECT produto, quantidade
        FROM estoque
        WHERE quantidade < 10
        ORDER BY quantidade ASC
        LIMIT 5
        """)
        baixo = cursor.fetchall()

        baixo_nomes = [b[0] if b[0] else "Sem nome" for b in baixo]
        baixo_valores = [b[1] if b[1] else 0 for b in baixo]

        # ===== DATA =====
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
                        <input type="date" name="inicio" min="2020-01-01" max="2030-12-31">
                    </div>

                    <div class="campo">
                        <label>Até</label>
                        <input type="date" name="fim" min="2020-01-01" max="2030-12-31">
                    </div>

                    <button>Filtrar</button>
                </form>
            </div>

            <!-- ALERTA -->
            {"<div class='alerta-topo'>⚠️ Atenção: " + str(len(baixo_nomes)) + " produto(s) com estoque abaixo do mínimo</div>" if baixo_nomes else ""}

            <!-- KPI -->
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

            <!-- GRÁFICOS -->
            <div class="grid">
                <div class="box"><h3>📊 Distribuição</h3><canvas id="pizza"></canvas></div>
                <div class="box"><h3>📈 Movimentações</h3><canvas id="linha"></canvas></div>
                <div class="box"><h3>🔥 Top Produtos</h3><canvas id="top"></canvas></div>
                <div class="box"><h3>⚠️ Baixo Estoque</h3><canvas id="baixo"></canvas></div>
            </div>

        </div>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <script>
        const cores = [
            "#38bdf8",
            "#60a5fa",
            "#818cf8",
            "#a78bfa",
            "#22d3ee"
        ];

        const baseOptions = {{
            responsive:true,
            maintainAspectRatio:false,
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

        .topo-dashboard{{
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:15px;
        }}

        .subtitulo{{
            color:#64748b;
            font-size:13px;
        }}

        .filtro-data{{
            display:flex;
            gap:10px;
            align-items:end;
        }}

        .campo{{
            display:flex;
            flex-direction:column;
            font-size:12px;
            color:#94a3b8;
        }}

        .filtro-data input{{
            background:#020617;
            border:1px solid #1e293b;
            padding:8px;
            color:white;
            border-radius:6px;
        }}

        .filtro-data button{{
            background:linear-gradient(90deg,#38bdf8,#0ea5e9);
            border:none;
            padding:8px 15px;
            border-radius:6px;
            cursor:pointer;
        }}

        .alerta-topo{{
            background:#7f1d1d;
            padding:10px;
            border-radius:8px;
            margin-bottom:15px;
            color:#fecaca;
            text-align:center;
        }}

        .cards{{
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:15px;
            margin-bottom:20px
        }}

        .card{{
            position:relative;
            overflow:hidden;
            background:linear-gradient(145deg,#0f172a,#020617);
            padding:20px;
            border-radius:15px;
            text-align:center;
            transition:0.3s;
        }}

        .card::after{{
            content:'';
            position:absolute;
            top:0;
            left:0;
            width:100%;
            height:2px;
            background:linear-gradient(90deg,#38bdf8,#0ea5e9);
        }}

        .card:hover{{
            transform:translateY(-5px);
            box-shadow:0 0 25px #38bdf8;
        }}

        .card h1{{
            font-size:40px;
            font-weight:700;
        }}

        .azul{{color:#38bdf8}}

        .status{{
            display:inline-block;
            width:10px;
            height:10px;
            border-radius:50%;
            margin-right:6px;
        }}

        .status.on{{background:#00ff9c}}
        .status.off{{background:#ff4d4d}}

        .grid{{
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:20px
        }}

        .box{{
            background:#020617;
            padding:15px;
            border-radius:15px;
            height:380px;
        }}

        canvas{{
            width:100% !important;
            height:100% !important;
        }}

        @media(max-width:768px){{
            .cards{{grid-template-columns:1fr 1fr}}
            .grid{{grid-template-columns:1fr}}
        }}
        </style>
        """

        return container(html)

    finally:
        devolver_conexao(conn)
