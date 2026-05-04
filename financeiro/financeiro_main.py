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

    return container(f"""SEU HTML ORIGINAL AQUI""")
