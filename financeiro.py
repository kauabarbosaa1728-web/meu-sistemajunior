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
        tabela += f"""
        <tr>
            <td>R$ {float(d[0]):.2f}</td>
            <td>{d[1]}</td>
            <td>{d[2]}</td>
        </tr>
        """

    return container(f"""
    <div class="wrap">

        <h2>➕ Entradas</h2>

        <div class="box">
            <input id="busca" placeholder="🔍 Pesquisar..." onkeyup="filtrar()">

            <table id="tabela">
                <tr>
                    <th>Valor</th>
                    <th>Descrição</th>
                    <th>Data</th>
                </tr>
                {tabela}
            </table>
        </div>

    </div>

    <script>
    function filtrar(){{
        let v = document.getElementById("busca").value.toLowerCase();
        document.querySelectorAll("#tabela tr").forEach(tr=>{{
            tr.style.display = tr.innerText.toLowerCase().includes(v) ? "" : "none";
        }});
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
        tabela += f"""
        <tr>
            <td>R$ {float(d[0]):.2f}</td>
            <td>{d[1]}</td>
            <td>{d[2]}</td>
        </tr>
        """

    return container(f"""
    <div class="wrap">

        <h2>➖ Saídas</h2>

        <div class="box">
            <input id="busca" placeholder="🔍 Pesquisar..." onkeyup="filtrar()">

            <table id="tabela">
                <tr>
                    <th>Valor</th>
                    <th>Descrição</th>
                    <th>Data</th>
                </tr>
                {tabela}
            </table>
        </div>

    </div>

    <script>
    function filtrar(){{
        let v = document.getElementById("busca").value.toLowerCase();
        document.querySelectorAll("#tabela tr").forEach(tr=>{{
            tr.style.display = tr.innerText.toLowerCase().includes(v) ? "" : "none";
        }});
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

    </div>
    """)
