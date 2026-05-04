from flask import Blueprint, session, redirect, request
from banco import conectar, devolver_conexao
from layout import container

relatorios_bp = Blueprint("relatorios_bp", __name__)

# ================= RELATÓRIO GERAL =================
@relatorios_bp.route("/relatorio-geral")
def relatorio_geral():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM estoque")
        estoque = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM veiculos")
        veiculos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM manutencoes")
        manut = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM problemas")
        problemas = cursor.fetchone()[0]

        return container(f"""
        <div class="card">
            <h2>📊 Relatório Geral</h2>

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;">
                <div class="card">📦 Estoque<br><b>{estoque}</b></div>
                <div class="card">🚗 Veículos<br><b>{veiculos}</b></div>
                <div class="card">🔧 Manutenções<br><b>{manut}</b></div>
                <div class="card">🚨 Problemas<br><b>{problemas}</b></div>
            </div>
        </div>
        """)

    finally:
        devolver_conexao(conn)


# ================= ESTOQUE =================
@relatorios_bp.route("/historico_estoque")
def historico_estoque():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto, quantidade, categoria, valor FROM estoque")
    dados = cursor.fetchall()

    nomes = []
    valores = []

    linhas = ""
    for produto, qtd, categoria, valor in dados:
        nomes.append(produto)
        valores.append(qtd)

        linhas += f"""
        <tr>
            <td>{produto}</td>
            <td>{qtd}</td>
            <td>{categoria or '-'}</td>
            <td>R$ {valor or 0}</td>
        </tr>
        """

    return container(f"""
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <div class="card">
        <h2>📦 Estoque</h2>
        <canvas id="grafico"></canvas>
    </div>

    <div class="card">
        <table style="width:100%">
            <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Valor</th></tr>
            {linhas}
        </table>
    </div>

    <script>
    new Chart(document.getElementById('grafico'), {{
        type:'bar',
        data:{{
            labels:{nomes},
            datasets:[{{label:'Quantidade', data:{valores}}}]
        }}
    }});
    </script>
    """)


# ================= VEÍCULOS =================
@relatorios_bp.route("/relatorio-veiculos")
def relatorio_veiculos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT motorista, nome, placa, equipe FROM veiculos")
    dados = cursor.fetchall()

    linhas = ""
    for v in dados:
        linhas += f"""
        <tr>
            <td>{v[0]}</td>
            <td>{v[1]}</td>
            <td>{v[2]}</td>
            <td>{v[3]}</td>
        </tr>
        """

    return container(f"""
    <div class="card">
        <h2>🚗 Veículos</h2>

        <table style="width:100%">
        <tr>
        <th>Motorista</th>
        <th>Nome</th>
        <th>Placa</th>
        <th>Equipe</th>
        </tr>
        {linhas}
        </table>
    </div>
    """)


# ================= FINANCEIRO =================
@relatorios_bp.route("/relatorio-financeiro")
def financeiro():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(valor) FROM manutencoes")
    total = cursor.fetchone()[0] or 0

    return container(f"""
    <div class="card">
        <h2>💸 Financeiro</h2>
        <h1 style="color:#22c55e;">R$ {total:.2f}</h1>
    </div>
    """)


# ================= PROBLEMAS =================
@relatorios_bp.route("/relatorio-problemas")
def problemas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT tipo, status FROM problemas")
    dados = cursor.fetchall()

    tipos = [d[0] for d in dados]

    return container(f"""
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <div class="card">
        <h2>🚨 Problemas</h2>
        <canvas id="grafico"></canvas>
    </div>

    <script>
    new Chart(document.getElementById('grafico'), {{
        type:'pie',
        data:{{
            labels:{tipos},
            datasets:[{{data:[1,1,1,1,1]}}]
        }}
    }});
    </script>
    """)
