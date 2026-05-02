from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from veiculos.layout_veiculos import container
from werkzeug.utils import secure_filename
import os
from datetime import datetime

problemas_bp = Blueprint("problemas_bp", __name__)

UPLOAD_FOLDER = "static/uploads"

@problemas_bp.route("/problemas", methods=["GET", "POST"])
def problemas():

    if "user" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    try:

        # SALVAR PROBLEMA
        if request.method == "POST":
            tipo = request.form.get("tipo")
            descricao = request.form.get("descricao")
            arquivo = request.files.get("foto")

            caminho_foto = ""

            if arquivo and arquivo.filename != "":
                nome = secure_filename(arquivo.filename)
                caminho_foto = os.path.join(UPLOAD_FOLDER, nome)
                arquivo.save(caminho_foto)

            cursor.execute("""
                INSERT INTO problemas (tipo, descricao, foto, data)
                VALUES (%s, %s, %s, %s)
            """, (tipo, descricao, caminho_foto, datetime.now()))

            conn.commit()

        # LISTAR
        cursor.execute("""
            SELECT tipo, descricao, foto, data
            FROM problemas
            ORDER BY data DESC
        """)

        dados = cursor.fetchall()

        lista = ""
        for d in dados:
            lista += f"""
            <div class='card'>
                <b>Problema:</b> {d[0]}<br>
                <b>Descrição:</b> {d[1]}<br>
                <b>Data:</b> {d[3]}<br>
                {"<img src='/" + d[2] + "' style='max-width:200px'>" if d[2] else ""}
            </div>
            """

        return container(f"""

        <h2>🚨 Registrar Problema</h2>

        <form method="POST" enctype="multipart/form-data">

            <label>Qual foi o problema?</label>
            <select name="tipo" required>
                <option>Pneu furado</option>
                <option>Sem gasolina</option>
                <option>Não identificado</option>
                <option>Carro esquentou</option>
                <option>Carro não liga</option>
            </select>

            <label>Foto</label>
            <input type="file" name="foto">

            <label>Descrição</label>
            <textarea name="descricao" placeholder="Explique o que aconteceu"></textarea>

            <button>Enviar Problema</button>

        </form>

        <hr>

        <h3>📋 Histórico</h3>

        {lista}

        """)

    except Exception as e:
        return container(f"<pre>{str(e)}</pre>")

    finally:
        cursor.close()
        devolver_conexao(conn)
