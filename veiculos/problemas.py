from flask import Blueprint, request, redirect, session, send_file
from banco import conectar, devolver_conexao
from veiculos.layout_veiculos import container
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io

problemas_bp = Blueprint("problemas_bp", __name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= REGISTRAR =================
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

            if arquivo and arquivo.filename:
                nome = secure_filename(arquivo.filename)
                caminho_foto = os.path.join(UPLOAD_FOLDER, nome)
                arquivo.save(caminho_foto)

            cursor.execute("""
                INSERT INTO problemas (tipo, descricao, foto, data, usuario, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo, descricao, caminho_foto, agora, usuario, 'aberto'))

            conn.commit()

        return container("""
        <h2>🚨 Registrar Problema</h2>

        <form method="POST" enctype="multipart/form-data">
            <label>Problema:</label>
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

            <button>Enviar</button>
        </form>
        """)

    except Exception as e:
        return container(f"<pre>{str(e)}</pre>")

    finally:
        cursor.close()
        devolver_conexao(conn)


# ================= LISTA =================
@problemas_bp.route("/problemas-lista")
def problemas_lista():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT id, tipo, descricao, foto, data, usuario, status
        FROM problemas
        ORDER BY data DESC
        """)

        dados = cursor.fetchall()
        lista = ""

        for d in dados:

            data_formatada = d[4].strftime('%d/%m/%Y %H:%M') if d[4] else "Sem data"
            usuario = d[5] or "Desconhecido"
            status = d[6] or "aberto"

            lista += f"""
            <div class="card">
                <h3>🚨 {d[1]}</h3>

                <p><b>Usuário:</b> {usuario}</p>
                <p><b>Data:</b> {data_formatada}</p>

                <p>{d[2]}</p>

                {"<img src='/" + d[3] + "' style='max-width:250px'>" if d[3] else ""}

                <br><br>

                <p>Status: {"🟢 Resolvido" if status=='resolvido' else "🔴 Aberto"}</p>

                <a href="/resolver/{d[0]}">✅ Resolver</a><br>
                <a href="/deletar-problema/{d[0]}" onclick="return confirm('Tem certeza?')">🗑️ Deletar</a><br>

                <!-- 🔥 NOVA ROTA -->
                <a href="/pdf/{d[0]}">📄 Baixar PDF</a>
            </div>
            """

        return container(f"""
        <h2>📋 Ocorrências</h2>
        {lista if lista else "<p>Nenhum problema registrado.</p>"}
        """)

    except Exception as e:
        return container(f"<pre>{str(e)}</pre>")

    finally:
        cursor.close()
        devolver_conexao(conn)


# ================= RESOLVER =================
@problemas_bp.route("/resolver/<int:id>")
def resolver(id):

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE problemas SET status='resolvido' WHERE id=%s
        """, (id,))
        conn.commit()

    except Exception as e:
        return container(f"<pre>{str(e)}</pre>")

    finally:
        cursor.close()
        devolver_conexao(conn)

    return redirect("/problemas-lista")


# ================= PDF FINAL =================
@problemas_bp.route("/pdf/<int:id>")
def baixar_pdf(id):

    print("🔥 PDF NOVO SENDO USADO 🔥")

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT tipo, descricao, usuario, data, status
        FROM problemas WHERE id=%s
        """, (id,))
        d = cursor.fetchone()

        if not d:
            return "REGISTRO NÃO ENCONTRADO"

        tipo, descricao, usuario, data, status = d

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 760, "RELATÓRIO DE OCORRÊNCIA")

        c.setStrokeColor(colors.blue)
        c.setLineWidth(2)
        c.line(100, 750, 450, 750)

        c.setFont("Helvetica", 12)
        c.drawString(100, 720, f"Problema: {tipo}")
        c.drawString(100, 700, f"Usuário: {usuario}")
        c.drawString(100, 680, f"Data: {data}")
        c.drawString(100, 660, f"Descrição: {descricao}")

        if status == "resolvido":
            c.setFillColor(colors.green)
            c.drawString(100, 630, "✔ RESOLVIDO")
        else:
            c.setFillColor(colors.red)
            c.drawString(100, 630, "⚠ EM ABERTO")

        c.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"ocorrencia_{id}.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        return f"ERRO REAL: {str(e)}"

    finally:
        cursor.close()
        devolver_conexao(conn)


# ================= DELETAR =================
@problemas_bp.route("/deletar-problema/<int:id>")
def deletar_problema(id):

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM problemas WHERE id=%s", (id,))
        conn.commit()
    except Exception as e:
        return container(f"<pre>{str(e)}</pre>")
    finally:
        cursor.close()
        devolver_conexao(conn)

    return redirect("/problemas-lista")
