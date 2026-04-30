from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import container

veiculos_bp = Blueprint("veiculos_bp", __name__)

@veiculos_bp.route("/veiculos", methods=["GET", "POST"])
def veiculos_page():

    if "user" not in session:
        return redirect("/")

    empresa_id = session.get("empresa_id")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        placa = request.form.get("placa")
        nome = request.form.get("nome")

        cursor.execute("""
        INSERT INTO veiculos (placa, nome, empresa_id)
        VALUES (%s, %s, %s)
        """, (placa, nome, empresa_id))

        conn.commit()
        return redirect("/veiculos")

    cursor.execute("""
    SELECT placa, nome
    FROM veiculos
    WHERE empresa_id=%s
    """, (empresa_id,))

    dados = cursor.fetchall()

    lista_html = ""
    for v in dados:
        lista_html += f"""
        <li style="margin:8px 0;">
            🚗 <b>{v[0]}</b> - {v[1]}
        </li>
        """

    cursor.close()
    devolver_conexao(conn)

    return container(f"""
        <h2>🚗 Veículos</h2>

        <form method="POST">
            <input name="placa" placeholder="Placa" required>
            <input name="nome" placeholder="Nome do veículo" required>
            <button>Cadastrar</button>
        </form>

        <h3>Lista de veículos:</h3>
        <ul>
            {lista_html}
        </ul>
    """)
