from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import container, acesso_negado
import json

financeiro_bp = Blueprint("financeiro_bp", __name__)


@financeiro_bp.route("/financeiro", methods=["GET", "POST"])
def financeiro():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    mensagem = ""

    # ================= CADASTRAR =================
    if request.method == "POST":
        try:
            tipo = request.form.get("tipo")
            valor = float(request.form.get("valor"))
            descricao = request.form.get("descricao")

            cursor.execute("""
                INSERT INTO financeiro (tipo, valor, descricao, usuario)
                VALUES (%s, %s, %s, %s)
            """, (tipo, valor, descricao, session["user"]))

            conn.commit()
            mensagem = "✅ Registrado com sucesso!"

        except Exception as e:
            mensagem = f"Erro: {str(e)}"

    # ================= BUSCAR =================
    cursor.execute("""
        SELECT id, tipo, valor, descricao, data
        FROM financeiro
        WHERE usuario = %s
        ORDER BY id DESC
    """, (session["user"],))

    dados = cursor.fetchall()

    # ================= CALCULAR =================
    total_entrada = sum([float(d[2]) for d in dados if d[1] == "entrada"])
    total_saida = sum([float(d[2]) for d in dados if d[1] == "saida"])
    saldo = total_entrada - total_saida

    # ================= TABELA =================
    tabela = ""
    for d in dados:
        cor = "#22c55e" if d[1] == "entrada" else "#ef4444"

        tabela += f"""
        <tr>
            <td>{d[0]}</td>
            <td style="color:{cor}; font-weight:bold;">{d[1].upper()}</td>
            <td>R$ {float(d[2]):.2f}</td>
            <td>{d[3]}</td>
            <td>{d[4]}</td>
        </tr>
        """

    devolver_conexao(conn)

    labels_json = json.dumps(["Entradas", "Saídas"])
    valores_json = json.dumps([total_entrada, total_saida])

    return container(f"""
    <div class="wrap">

        <h2 style="margin-bottom:20px;">💰 Financeiro</h2>

        <input id="busca" placeholder="🔍 Pesquisar..." onkeyup="filtrar()" style="margin-bottom:15px;">

        <div class="cards">

            <div class="card green">
                <h3>Entradas</h3>
                <p>R$ {total_entrada:.2f}</p>
            </div>

            <div class="card red">
                <h3>Saídas</h3>
                <p>R$ {total_saida:.2f}</p>
            </div>

            <div class="card blue">
                <h3>Saldo</h3>
                <p>R$ {saldo:.2f}</p>
            </div>

        </div>

        <div class="box" style="margin-bottom:20px;">
            <h3>📊 Visão Financeira</h3>
            <canvas id="graficoFinanceiro"></canvas>
        </div>

        <div class="grid">

            <div class="box">
                <h3>➕ Nova movimentação</h3>

                <form method="POST">
                    <select name="tipo" required>
                        <option value="entrada">Entrada</option>
                        <option value="saida">Saída</option>
                    </select>

                    <input type="number" step="0.01" name="valor" placeholder="Valor" required>
                    <input type="text" name="descricao" placeholder="Descrição">

                    <button>Salvar</button>
                </form>

                <p>{mensagem}</p>
            </div>

            <div class="box">
                <h3>📋 Histórico</h3>

                <table id="tabela">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tipo</th>
                            <th>Valor</th>
                            <th>Descrição</th>
                            <th>Data</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tabela}
                    </tbody>
                </table>
            </div>

        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    new Chart(document.getElementById('graficoFinanceiro'), {{
        type: 'bar',
        data: {{
            labels: {labels_json},
            datasets: [{{
                data: {valores_json},
                backgroundColor: ["#22c55e", "#ef4444"],
                borderRadius: 12
            }}]
        }},
        options: {{
            responsive:true,
            maintainAspectRatio:false,
            animation:{{duration:1200}},
            plugins: {{
                legend: {{display:false}}
            }}
        }}
    }});

    function filtrar(){{
        let input = document.getElementById("busca").value.toLowerCase();
        let linhas = document.querySelectorAll("#tabela tbody tr");

        linhas.forEach(l => {{
            l.style.display = l.innerText.toLowerCase().includes(input) ? "" : "none";
        }});
    }}
    </script>

    <style>
    .wrap {{
        max-width: 1300px;
        margin: auto;
    }}

    .cards {{
        display:flex;
        gap:15px;
        margin-bottom:20px;
    }}

    .card {{
        flex:1;
        padding:20px;
        border-radius:12px;
        text-align:center;
        background:#020617;
        border:1px solid rgba(56,189,248,0.2);
    }}

    .card p {{
        font-size:22px;
        margin-top:10px;
        font-weight:bold;
    }}

    .green {{ border-left:4px solid #22c55e; }}
    .red {{ border-left:4px solid #ef4444; }}
    .blue {{ border-left:4px solid #3b82f6; }}

    .grid {{
        display:grid;
        grid-template-columns:300px 1fr;
        gap:20px;
    }}

    .box {{
        background:#020617;
        border:1px solid #1e293b;
        padding:20px;
        border-radius:12px;
    }}

    canvas {{
        width:100% !important;
        height:250px !important;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
    }}

    th {{
        background:#1a1a1a;
        padding:10px;
        text-align:left;
    }}

    td {{
        padding:10px;
        border-top:1px solid #333;
    }}

    tr:hover {{
        background:#111;
    }}

    @media(max-width: 850px) {{
        .cards, .grid {{
            display:block;
        }}

        .card, .box {{
            margin-bottom:15px;
        }}
    }}
    </style>
    """)


# ================= ENTRADAS =================
@financeiro_bp.route("/entrada-financeiro")
def entrada_financeiro():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT valor, descricao, data
        FROM financeiro
        WHERE tipo = 'entrada' AND usuario = %s
        ORDER BY id DESC
    """, (session["user"],))

    dados = cursor.fetchall()
    devolver_conexao(conn)

    total_entradas = sum([float(d[0]) for d in dados])
    registros = len(dados)

    tabela = ""
    for d in dados:
        tabela += f"""
        <tr>
            <td>R$ {float(d[0]):.2f}</td>
            <td>{d[1]}</td>
            <td>{d[2]}</td>
        </tr>
        """

    labels_json = json.dumps([str(d[2])[:10] for d in dados])
    valores_json = json.dumps([float(d[0]) for d in dados])

    return container(f"""
    <div class="wrap">

        <h2>➕ Entradas</h2>

        <div class="cards">
            <div class="card green">
                <h3>Total de Entradas</h3>
                <p>R$ {total_entradas:.2f}</p>
            </div>

            <div class="card blue">
                <h3>Registros</h3>
                <p>{registros}</p>
            </div>
        </div>

        <div class="box filtros">
            <input id="busca" placeholder="🔍 Buscar entrada..." onkeyup="filtrar()">

            <div class="filtro-data">
                <input type="date" id="dataInicio" onchange="filtrar()">
                <input type="date" id="dataFim" onchange="filtrar()">
            </div>

            <button type="button" onclick="limparFiltros()">Limpar filtros</button>
        </div>

        <div class="box">
            <h3>📊 Entradas ao longo do tempo</h3>
            <canvas id="graficoEntradas"></canvas>
        </div>

        <div class="box tabela-box">
            <table id="tabela">
                <thead>
                    <tr>
                        <th>💰 Valor</th>
                        <th>📝 Descrição</th>
                        <th>📅 Data</th>
                    </tr>
                </thead>

                <tbody>
                    {tabela}
                </tbody>
            </table>
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    function filtrar(){{
        let texto = document.getElementById("busca").value.toLowerCase();
        let inicio = document.getElementById("dataInicio").value;
        let fim = document.getElementById("dataFim").value;

        document.querySelectorAll("#tabela tbody tr").forEach(tr=>{{
            let conteudo = tr.innerText.toLowerCase();
            let data = tr.children[2].innerText.substring(0,10);

            let mostrar = conteudo.includes(texto);

            if(inicio && data < inicio) mostrar = false;
            if(fim && data > fim) mostrar = false;

            tr.style.display = mostrar ? "" : "none";
        }});
    }}

    function limparFiltros(){{
        document.getElementById("busca").value = "";
        document.getElementById("dataInicio").value = "";
        document.getElementById("dataFim").value = "";
        filtrar();
    }}

    new Chart(document.getElementById('graficoEntradas'), {{
        type: 'line',
        data: {{
            labels: {labels_json},
            datasets: [{{
                label: 'Entradas',
                data: {valores_json},
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34,197,94,0.18)',
                fill: true,
                tension: 0.4,
                pointRadius: 4
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
        max-width: 1300px;
        margin: auto;
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

    .filtros {{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        align-items:center;
    }}

    .filtros input {{
        flex:1;
        min-width:220px;
    }}

    .filtro-data {{
        display:flex;
        gap:10px;
    }}

    input {{
        padding:12px;
        border-radius:10px;
        background:#0b0f1a;
        color:white;
        border:1px solid #334155;
    }}

    button {{
        padding:12px 16px;
        background:#2563eb;
        border:none;
        border-radius:10px;
        color:white;
        cursor:pointer;
        font-weight:bold;
    }}

    button:hover {{
        background:#1d4ed8;
    }}

    .tabela-box {{
        max-height:430px;
        overflow:auto;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
    }}

    thead {{
        position:sticky;
        top:0;
        background:#111827;
        z-index:2;
    }}

    th {{
        padding:14px;
        text-align:left;
        color:#93c5fd;
        border-bottom:1px solid rgba(255,255,255,0.08);
    }}

    td {{
        padding:14px;
        border-top:1px solid #1f2937;
    }}

    tbody tr:hover {{
        background:rgba(34,197,94,0.08);
    }}

    td:first-child {{
        color:#22c55e;
        font-weight:bold;
    }}

    canvas {{
        width:100% !important;
        height:280px !important;
    }}

    @media(max-width: 850px) {{
        .cards, .filtros, .filtro-data {{
            display:block;
        }}

        .card, .box, .filtros input, .filtro-data input, button {{
            width:100%;
            margin-bottom:10px;
        }}
    }}
    </style>
    """)


# ================= SAIDAS =================
@financeiro_bp.route("/saida-financeiro")
def saida_financeiro():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT valor, descricao, data
        FROM financeiro
        WHERE tipo = 'saida' AND usuario = %s
        ORDER BY id DESC
    """, (session["user"],))

    dados = cursor.fetchall()
    devolver_conexao(conn)

    total_saidas = sum([float(d[0]) for d in dados])
    registros = len(dados)

    tabela = ""
    for d in dados:
        tabela += f"""
        <tr>
            <td>R$ {float(d[0]):.2f}</td>
            <td>{d[1]}</td>
            <td>{d[2]}</td>
        </tr>
        """

    labels_json = json.dumps([str(d[2])[:10] for d in dados])
    valores_json = json.dumps([float(d[0]) for d in dados])

    return container(f"""
    <div class="wrap">

        <h2>➖ Saídas</h2>

        <div class="cards">
            <div class="card red">
                <h3>Total de Saídas</h3>
                <p>R$ {total_saidas:.2f}</p>
            </div>

            <div class="card blue">
                <h3>Registros</h3>
                <p>{registros}</p>
            </div>
        </div>

        <div class="box filtros">
            <input id="busca" placeholder="🔍 Buscar saída..." onkeyup="filtrar()">

            <div class="filtro-data">
                <input type="date" id="dataInicio" onchange="filtrar()">
                <input type="date" id="dataFim" onchange="filtrar()">
            </div>

            <button type="button" onclick="limparFiltros()">Limpar filtros</button>
        </div>

        <div class="box">
            <h3>📉 Saídas ao longo do tempo</h3>
            <canvas id="graficoSaidas"></canvas>
        </div>

        <div class="box tabela-box">
            <table id="tabela">
                <thead>
                    <tr>
                        <th>💸 Valor</th>
                        <th>📝 Descrição</th>
                        <th>📅 Data</th>
                    </tr>
                </thead>

                <tbody>
                    {tabela}
                </tbody>
            </table>
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    function filtrar(){{
        let texto = document.getElementById("busca").value.toLowerCase();
        let inicio = document.getElementById("dataInicio").value;
        let fim = document.getElementById("dataFim").value;

        document.querySelectorAll("#tabela tbody tr").forEach(tr=>{{
            let conteudo = tr.innerText.toLowerCase();
            let data = tr.children[2].innerText.substring(0,10);

            let mostrar = conteudo.includes(texto);

            if(inicio && data < inicio) mostrar = false;
            if(fim && data > fim) mostrar = false;

            tr.style.display = mostrar ? "" : "none";
        }});
    }}

    function limparFiltros(){{
        document.getElementById("busca").value = "";
        document.getElementById("dataInicio").value = "";
        document.getElementById("dataFim").value = "";
        filtrar();
    }}

    new Chart(document.getElementById('graficoSaidas'), {{
        type: 'line',
        data: {{
            labels: {labels_json},
            datasets: [{{
                label: 'Saídas',
                data: {valores_json},
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239,68,68,0.18)',
                fill: true,
                tension: 0.4,
                pointRadius: 4
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
        max-width: 1300px;
        margin: auto;
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

    .filtros {{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        align-items:center;
    }}

    .filtros input {{
        flex:1;
        min-width:220px;
    }}

    .filtro-data {{
        display:flex;
        gap:10px;
    }}

    input {{
        padding:12px;
        border-radius:10px;
        background:#0b0f1a;
        color:white;
        border:1px solid #334155;
    }}

    button {{
        padding:12px 16px;
        background:#2563eb;
        border:none;
        border-radius:10px;
        color:white;
        cursor:pointer;
        font-weight:bold;
    }}

    button:hover {{
        background:#1d4ed8;
    }}

    .tabela-box {{
        max-height:430px;
        overflow:auto;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
    }}

    thead {{
        position:sticky;
        top:0;
        background:#111827;
        z-index:2;
    }}

    th {{
        padding:14px;
        text-align:left;
        color:#93c5fd;
        border-bottom:1px solid rgba(255,255,255,0.08);
    }}

    td {{
        padding:14px;
        border-top:1px solid #1f2937;
    }}

    tbody tr:hover {{
        background:rgba(239,68,68,0.08);
    }}

    td:first-child {{
        color:#ef4444;
        font-weight:bold;
    }}

    canvas {{
        width:100% !important;
        height:280px !important;
    }}

    @media(max-width: 850px) {{
        .cards, .filtros, .filtro-data {{
            display:block;
        }}

        .card, .box, .filtros input, .filtro-data input, button {{
            width:100%;
            margin-bottom:10px;
        }}
    }}
    </style>
    """)


# ================= RESUMO =================
@financeiro_bp.route("/resumo-financeiro")
def resumo_financeiro():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada' AND usuario=%s", (session["user"],))
    entradas = float(cursor.fetchone()[0])

    cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida' AND usuario=%s", (session["user"],))
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
