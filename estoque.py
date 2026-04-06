from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao, registrar_log
from layout import container, acesso_negado, tem_permissao

from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from openpyxl import Workbook

estoque_bp = Blueprint("estoque_bp", __name__)

# ================= ESTOQUE =================
@estoque_bp.route("/estoque", methods=["GET", "POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")
        fornecedor = request.form.get("fornecedor")
        valor = request.form.get("valor")

        if produto and qtd and categoria:
            try:
                qtd = int(qtd)
                valor = float(valor or 0)

                cursor.execute("""
                INSERT INTO estoque (produto, quantidade, categoria, valor)
                VALUES (%s,%s,%s,%s)
                """, (produto, qtd, categoria, valor))

                conn.commit()
                registrar_log(session["user"], "add_estoque", produto)

                msg = "✅ Adicionado"

            except Exception as e:
                conn.rollback()
                msg = f"❌ Erro: {e}"

    cursor.execute("SELECT id, produto, quantidade, categoria, valor FROM estoque ORDER BY id DESC")
    dados = cursor.fetchall()

    total_qtd = sum([d[2] for d in dados])
    total_valor = sum([d[2] * float(d[4] or 0) for d in dados])

    tabela = ""
    for i, p, q, c, v in dados:
        tabela += f"""
        <tr>
        <td>{i}</td>
        <td>{p}</td>
        <td>{q}</td>
        <td>{c}</td>
        <td>R$ {float(v or 0):,.2f}</td>
        <td>
        <a href='/editar_estoque/{i}'>✏️ Editar</a> |
        <a href='/excluir_estoque/{i}' onclick="return confirm('Tem certeza?')">🗑️ Excluir</a>
        </td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>📦 ESTOQUE</h2>

    <div style="margin-bottom:15px; padding:10px; background:#111; border-radius:8px;">
        <b>Quantidade total:</b> {total_qtd} <br>
        <b>Custo total:</b> R$ {total_valor:,.2f}
    </div>

    <a href="/entrada">➕ Entrada de Produtos</a>

    <form method="POST" style="display:flex; flex-direction:column; gap:10px; max-width:300px;">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="categoria" placeholder="Categoria">
        <input name="fornecedor" placeholder="Fornecedor">
        <input name="valor" placeholder="Valor (R$)">
        <button>Adicionar</button>
    </form>

    <p>{msg}</p>

    <table>
    <tr>
    <th>ID</th><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Valor</th><th>Ações</th>
    </tr>
    {tabela}
    </table>
    </div>
    """)


# ================= EDITAR =================
@estoque_bp.route("/editar_estoque/<int:id>", methods=["GET", "POST"])
def editar_estoque(id):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")
        valor = request.form.get("valor")

        try:
            qtd = int(qtd)
            valor = float(valor or 0)

            cursor.execute("""
            UPDATE estoque 
            SET produto=%s, quantidade=%s, categoria=%s, valor=%s
            WHERE id=%s
            """, (produto, qtd, categoria, valor, id))

            conn.commit()
            registrar_log(session["user"], "editar_estoque", produto)

            devolver_conexao(conn)
            return redirect("/estoque")

        except Exception as e:
            conn.rollback()
            return container(f"""
            <div class="card">
            <h2 style='color:red'>❌ Erro ao atualizar</h2>
            <p>{e}</p>
            <a href="/estoque">⬅ Voltar</a>
            </div>
            """)

    cursor.execute("SELECT produto, quantidade, categoria, valor FROM estoque WHERE id=%s", (id,))
    dado = cursor.fetchone()

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>✏️ EDITAR PRODUTO</h2>

    <form method="POST">
        <input name="produto" value="{dado[0]}">
        <input name="qtd" value="{dado[1]}">
        <input name="categoria" value="{dado[2]}">
        <input name="valor" value="{float(dado[3] or 0):.2f}">
        <button>Salvar</button>
    </form>
    </div>
    """)


# ================= EXCLUIR =================
@estoque_bp.route("/excluir_estoque/<int:id>")
def excluir_estoque(id):
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_excluir_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM estoque WHERE id=%s", (id,))
    conn.commit()

    registrar_log(session["user"], "excluir_estoque", str(id))

    devolver_conexao(conn)
    return redirect("/estoque")


# ================= TRANSFERENCIA =================
@estoque_bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    cursor.execute("SELECT produto FROM estoque")
    produtos = [p[0] for p in cursor.fetchall()]

    cursor.execute("SELECT usuario FROM usuarios")
    usuarios = [u[0] for u in cursor.fetchall()]

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])
        destino = request.form.get("destino")

        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
        dado = cursor.fetchone()

        if dado and dado[0] >= qtd:
            cursor.execute(
                "UPDATE estoque SET quantidade=%s WHERE produto=%s",
                (dado[0] - qtd, produto)
            )

            cursor.execute("""
            INSERT INTO transferencias (produto,quantidade,origem,destino,usuario)
            VALUES (%s,%s,%s,%s,%s)
            """, (produto, qtd, "estoque", destino or "saida", session["user"]))

            conn.commit()
            registrar_log(session["user"], "transferencia", produto)

            msg = "✅ Transferência realizada"
        else:
            msg = "❌ Estoque insuficiente"

    lista_produtos = "".join([f"<option value='{p}'>{p}</option>" for p in produtos])
    lista_usuarios = "".join([f"<option value='{u}'>{u}</option>" for u in usuarios])

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>🔄 TRANSFERÊNCIA</h2>

    <form method="POST">
        <select name="produto">{lista_produtos}</select>
        <input name="qtd">
        <select name="destino">{lista_usuarios}</select>
        <button>Transferir</button>
    </form>

    <p>{msg}</p>
    </div>
    """)
