from flask import redirect, session
from banco import conectar, devolver_conexao
from layout import container
from . import financeiro_bp
import json

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

    return container(f"""SEU HTML ORIGINAL AQUI""")
