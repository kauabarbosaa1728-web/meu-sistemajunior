from flask import request, redirect, session
from banco import conectar, devolver_conexao
from layout import container
from . import financeiro_bp
import json

@financeiro_bp.route("/financeiro", methods=["GET", "POST"])
def financeiro():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    mensagem = ""

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

    cursor.execute("""
        SELECT id, tipo, valor, descricao, data
        FROM financeiro
        WHERE usuario = %s
        ORDER BY id DESC
    """, (session["user"],))

    dados = cursor.fetchall()

    total_entrada = sum([float(d[2]) for d in dados if d[1] == "entrada"])
    total_saida = sum([float(d[2]) for d in dados if d[1] == "saida"])
    saldo = total_entrada - total_saida

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
    """)
