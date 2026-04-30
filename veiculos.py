from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import container

veiculos_bp = Blueprint("veiculos_bp", __name__)

@veiculos_bp.route("/veiculos", methods=["GET", "POST"])
def veiculos():

    if "user" not in session:
        return redirect("/")

    empresa_id = session.get("empresa_id")

    if not empresa_id:
        return container("<h2>❌ Empresa não definida</h2>")

    conn = conectar()
    if conn is None:
        return "Erro ao conectar banco"

    try:
        cursor = conn.cursor()

        # CADASTRAR
        if request.method == "POST":
            placa = request.form.get("placa")

            cursor.execute("""
            INSERT INTO veiculos (placa, empresa_id)
            VALUES (%s, %s)
            """, (placa, empresa_id))

            conn.commit()
            return redirect("/veiculos")

        # LISTAR
        cursor.execute("""
        SELECT id, placa FROM veiculos
        WHERE empresa_id=%s
        ORDER BY id DESC
        """, (empresa_id,))

        dados = cursor.fetchall()

        lista = ""
        for d in dados:
            lista += f"<li>{d[1]}</li>"

    except Exception as e:
        return f"ERRO: {str(e)}"

    finally:
        cursor.close()
        devolver_conexao(conn)

    return container(f"""
        <h2>🚗 Veículos</h2>

        <form method="POST">
            <input name="placa" placeholder="Placa" required>
            <button>Salvar</button>
        </form>

        <h3>Lista:</h3>
        <ul>{lista}</ul>
    """)
