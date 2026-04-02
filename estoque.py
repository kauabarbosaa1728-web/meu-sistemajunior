from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao, registrar_log, verificar_pagamento
from layout import container, acesso_negado, tem_permissao

estoque_bp = Blueprint("estoque_bp", __name__)

# ================= ESTOQUE =================
@estoque_bp.route("/estoque", methods=["GET", "POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    # 🔥 NÃO BLOQUEIA ADMIN
    if session.get("cargo") != "admin":
        status = verificar_pagamento(session["user"])

        if status == "bloqueado":
            return "<h1 style='color:red;text-align:center;'>🚫 Sistema bloqueado</h1>"
        elif status == "aviso":
            aviso = "<div style='color:yellow;text-align:center;'>⚠️ Plano vencendo</div>"
        else:
            aviso = ""
    else:
        aviso = ""

    if not tem_permissao("pode_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")

        if produto and qtd and categoria:
            try:
                qtd = int(qtd)
                cursor.execute("""
                INSERT INTO estoque (produto, quantidade, categoria, valor)
                VALUES (%s,%s,%s,%s)
                """, (produto, qtd, categoria, 0))
                conn.commit()
                registrar_log(session["user"], "add_estoque", produto)
                msg = "✅ Adicionado"
            except Exception as e:
                msg = f"❌ Erro: {e}"

    cursor.execute("SELECT id, produto, quantidade, categoria, valor FROM estoque ORDER BY id DESC")
    dados = cursor.fetchall()

    tabela = ""
    for i,p,q,c,v in dados:
        tabela += f"""
        <tr>
        <td>{i}</td>
        <td>{p}</td>
        <td>{q}</td>
        <td>{c}</td>
        <td>R$ {float(v or 0):,.2f}</td>
        <td>
        <a href='/editar_estoque/{i}'>✏️</a> |
        <a href='/excluir_estoque/{i}'>🗑️</a>
        </td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    {aviso}
    <div class="card">
    <h2>📦 ESTOQUE</h2>

    <form method="POST">
    <input name="produto" placeholder="Produto">
    <input name="qtd" placeholder="Qtd">
    <input name="categoria" placeholder="Categoria">
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
@estoque_bp.route("/editar_estoque/<int:id>", methods=["GET","POST"])
def editar_estoque(id):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = int(request.form.get("qtd"))
        categoria = request.form.get("categoria")

        cursor.execute("""
        UPDATE estoque SET produto=%s, quantidade=%s, categoria=%s
        WHERE id=%s
        """, (produto, qtd, categoria, id))

        conn.commit()
        devolver_conexao(conn)
        return redirect("/estoque")

    cursor.execute("SELECT produto, quantidade, categoria FROM estoque WHERE id=%s",(id,))
    dado = cursor.fetchone()
    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>✏️ EDITAR</h2>
    <form method="POST">
    <input name="produto" value="{dado[0]}">
    <input name="qtd" value="{dado[1]}">
    <input name="categoria" value="{dado[2]}">
    <button>Salvar</button>
    </form>
    </div>
    """)

# ================= EXCLUIR =================
@estoque_bp.route("/excluir_estoque/<int:id>")
def excluir_estoque(id):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM estoque WHERE id=%s",(id,))
    conn.commit()

    devolver_conexao(conn)
    return redirect("/estoque")

# ================= TRANSFERENCIA =================
@estoque_bp.route("/transferencia", methods=["GET","POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    msg=""

    cursor.execute("SELECT produto FROM estoque")
    produtos = [p[0] for p in cursor.fetchall()]

    cursor.execute("SELECT usuario FROM usuarios")
    usuarios = [u[0] for u in cursor.fetchall()]

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])
        destino = request.form.get("destino")

        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s",(produto,))
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
            msg="✅ Transferido"
        else:
            msg="❌ Estoque insuficiente"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>🔁 TRANSFERÊNCIA</h2>

    <form method="POST">
    <select name="produto">
    {''.join([f"<option>{p}</option>" for p in produtos])}
    </select>

    <input name="qtd" type="number">

    <select name="destino">
    {''.join([f"<option>{u}</option>" for u in usuarios])}
    </select>

    <button>Transferir</button>
    </form>

    <p>{msg}</p>
    </div>
    """)

# ================= HISTÓRICO =================
@estoque_bp.route("/historico")
def historico():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT produto, quantidade, destino, usuario FROM transferencias
    ORDER BY id DESC
    """)

    dados = cursor.fetchall()

    tabela = ""
    for p,q,d,u in dados:
        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{d}</td><td>{u}</td></tr>"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>📊 HISTÓRICO</h2>
    <table>
    <tr><th>Produto</th><th>Qtd</th><th>Destino</th><th>Usuário</th></tr>
    {tabela}
    </table>
    </div>
    """)
