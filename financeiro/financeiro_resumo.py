from flask import redirect, session
from banco import conectar, devolver_conexao
from layout import container
from . import financeiro_bp
import json

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

    return container(f"""SEU HTML ORIGINAL AQUI""")
