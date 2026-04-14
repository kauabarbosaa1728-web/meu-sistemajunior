from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import container, acesso_negado

financeiro_bp = Blueprint("financeiro_bp", __name__)

# ================= FINANCEIRO =================
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
            tipo = request.form.get("tipo")  # entrada / saida
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

    # ================= BUSCAR DADOS =================
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

    html = f"""
    <h2>💰 Financeiro</h2>

    <p style='color:green;'>Entradas: R$ {total_entrada:.2f}</p>
    <p style='color:red;'>Saídas: R$ {total_saida:.2f}</p>
    <h3>Saldo: R$ {saldo:.2f}</h3>

    <hr>

    <h3>➕ Nova movimentação</h3>

    <form method="POST">
        <select name="tipo" required>
            <option value="entrada">Entrada</option>
            <option value="saida">Saída</option>
        </select>

        <input type="number" step="0.01" name="valor" placeholder="Valor" required>
        <input type="text" name="descricao" placeholder="Descrição">

        <button type="submit">Salvar</button>
    </form>

    <p>{mensagem}</p>

    <hr>

    <h3>📋 Histórico</h3>

    <table border="1" width="100%">
        <tr>
            <th>ID</th>
            <th>Tipo</th>
            <th>Valor</th>
            <th>Descrição</th>
            <th>Data</th>
        </tr>
    """

    for d in dados:
        html += f"""
        <tr>
            <td>{d[0]}</td>
            <td>{d[1]}</td>
            <td>R$ {float(d[2]):.2f}</td>
            <td>{d[3]}</td>
            <td>{d[4]}</td>
        </tr>
        """

    html += "</table>"

    devolver_conexao(conn)

    return container(html)
