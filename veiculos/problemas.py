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
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    try:

        if request.method == "POST":
            tipo = request.form.get("tipo")
            descricao = request.form.get("descricao")
            arquivo = request.files.get("foto")

            usuario = session.get("user")
            agora = datetime.now()

            caminho_foto = ""

            if arquivo and arquivo.filename != "":
                nome = secure_filename(arquivo.filename)
                caminho_foto = os.path.join(UPLOAD_FOLDER, nome)
                arquivo.save(caminho_foto)

            cursor.execute("""
                INSERT INTO problemas (tipo, descricao, foto, data, usuario, status)
                VALUES (%s, %s, %s, %s, %s, 'aberto')
            """, (tipo, descricao, caminho_foto, agora, usuario))

            conn.commit()

        return container("""
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
            <textarea name="descricao"></textarea>

            <button>Enviar Problema</button>

        </form>
        """)

    finally:
        cursor.close()
        devolver_conexao(conn)


# 🔥 LISTA DE PROBLEMAS (NOVA ABA)
@problemas_bp.route("/problemas-lista")
def problemas_lista():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, tipo, descricao, foto, data, usuario, status
    FROM problemas
    ORDER BY data DESC
    """)

    dados = cursor.fetchall()

    lista = ""

    for d in dados:
        lista += f"""
        <div class="card">
            <h3>🚨 {d[1]}</h3>

            <p><b>Usuário:</b> {d[5]}</p>
            <p><b>Data:</b> {d[4].strftime('%d/%m/%Y')}</p>
            <p><b>Hora:</b> {d[4].strftime('%H:%M')}</p>

            <p>{d[2]}</p>

            {"<img src='/" + d[3] + "' style='max-width:250px'>" if d[3] else ""}

            <br><br>

            <p>Status: {"🟢 Resolvido" if d[6]=='resolvido' else "🔴 Aberto"}</p>

            <a href="/resolver/{d[0]}">✅ Resolver</a>
        </div>
        """

    return container(f"""
    <h2>📋 Ocorrências</h2>
    {lista}
    """)


# 🔥 RESOLVER PROBLEMA
@problemas_bp.route("/resolver/<int:id>")
def resolver(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE problemas SET status='resolvido' WHERE id=%s
    """, (id,))

    conn.commit()

    return redirect("/problemas-lista")
