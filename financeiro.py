from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import container, acesso_negado

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

    entradas = [float(d[2]) for d in dados if d[1] == "entrada"]
    saidas = [float(d[2]) for d in dados if d[1] == "saida"]

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

    return container(f"""

    <div class="wrap">

        <h2 style="margin-bottom:20px;">💰 Financeiro</h2>

        <!-- 🔍 BUSCA -->
        <input id="busca" placeholder="🔍 Pesquisar..." onkeyup="filtrar()" style="margin-bottom:15px;">

        <!-- CARDS -->
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

        <!-- 🔥 GRÁFICO -->
        <div class="box" style="margin-bottom:20px;">
            <h3>📊 Visão Financeira</h3>
            <canvas id="graficoFinanceiro"></canvas>
        </div>

        <div class="grid">

            <!-- FORM -->
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

            <!-- TABELA -->
            <div class="box">
                <h3>📋 Histórico</h3>

                <table id="tabela">
                    <tr>
                        <th>ID</th>
                        <th>Tipo</th>
                        <th>Valor</th>
                        <th>Descrição</th>
                        <th>Data</th>
                    </tr>
                    {tabela}
                </table>
            </div>

        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
    new Chart(document.getElementById('graficoFinanceiro'), {{
        type: 'bar',
        data: {{
            labels: ["Entradas", "Saídas"],
            datasets: [{{
                data: [{total_entrada}, {total_saida}],
                backgroundColor: ["#22c55e", "#ef4444"]
            }}]
        }},
        options: {{
            responsive:true,
            maintainAspectRatio:false,
            animation:{{duration:1200}}
        }}
    }});

    function filtrar(){{
        let input = document.getElementById("busca").value.toLowerCase();
        let linhas = document.querySelectorAll("#tabela tr");

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

    input, select {{
        width:100%;
        padding:10px;
        margin-bottom:10px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    button {{
        width:100%;
        padding:10px;
        background:#3b82f6;
        border:none;
        border-radius:6px;
        color:white;
        cursor:pointer;
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

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>R$ {float(d[0]):.2f}</td><td>{d[1]}</td><td>{d[2]}</td></tr>"

    return container(f"""
    <div class="box">
        <h2>➕ Entradas</h2>

        <input id="busca" placeholder="🔍 Pesquisar..." onkeyup="filtrar()">

        <table id="tabela">
            <tr><th>Valor</th><th>Descrição</th><th>Data</th></tr>
            {tabela}
        </table>
    </div>

    <script>
    function filtrar(){{
        let v = document.getElementById("busca").value.toLowerCase();
        document.querySelectorAll("#tabela tr").forEach(tr=>{
            tr.style.display = tr.innerText.toLowerCase().includes(v) ? "" : "none";
        });
    }}
    </script>
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

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>R$ {float(d[0]):.2f}</td><td>{d[1]}</td><td>{d[2]}</td></tr>"

    return container(f"""
    <div class="box">
        <h2>➖ Saídas</h2>

        <input id="busca" placeholder="🔍 Pesquisar..." onkeyup="filtrar()">

        <table id="tabela">
            <tr><th>Valor</th><th>Descrição</th><th>Data</th></tr>
            {tabela}
        </table>
    </div>

    <script>
    function filtrar(){{
        let v = document.getElementById("busca").value.toLowerCase();
        document.querySelectorAll("#tabela tr").forEach(tr=>{
            tr.style.display = tr.innerText.toLowerCase().includes(v) ? "" : "none";
        });
    }}
    </script>
    """)


# ================= RESUMO =================
@financeiro_bp.route("/resumo-financeiro")
def resumo_financeiro():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada' AND usuario=%s", (session["user"],))
    entradas = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida' AND usuario=%s", (session["user"],))
    saidas = cursor.fetchone()[0]

    devolver_conexao(conn)

    saldo = entradas - saidas

    return container(f"""
    <div class="box">
        <h2>📊 Resumo Geral</h2>

        <p>💰 Entradas: R$ {entradas:.2f}</p>
        <p>💸 Saídas: R$ {saidas:.2f}</p>
        <h3>Saldo: R$ {saldo:.2f}</h3>
    </div>
    """)
