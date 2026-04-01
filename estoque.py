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

    total_qtd = sum([d[2] for d in dados])
    total_valor = sum([d[2] * float(d[4] or 0) for d in dados])

    tabela = ""
    for i,p,q,c,v in dados:
        tabela += f"""
        <tr>
        <td>{i}</td>
        <td>{p}</td>
        <td>{q}</td>
        <td>{c}</td>
        <td>R$ {float(v):,.2f}</td>
        <td>
        <a href='/editar_estoque/{i}'>Editar</a>
        <a href='/excluir_estoque/{i}'>Excluir</a>
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

# ================= ENTRADA =================
@estoque_bp.route("/entrada", methods=["GET", "POST"])
def entrada():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        valor = request.form.get("valor")
        fornecedor = request.form.get("fornecedor")

        try:
            qtd = int(qtd)
            valor = valor.replace("R$", "").replace(",", ".").strip()
            valor = float(valor)

            cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
            dado = cursor.fetchone()

            if dado:
                nova_qtd = dado[0] + qtd
                cursor.execute("UPDATE estoque SET quantidade=%s, valor=%s WHERE produto=%s",
                               (nova_qtd, valor, produto))
            else:
                cursor.execute("""
                INSERT INTO estoque (produto, quantidade, categoria, valor)
                VALUES (%s,%s,%s,%s)
                """, (produto, qtd, "entrada", valor))

            cursor.execute("""
            INSERT INTO entradas (produto, quantidade, valor, fornecedor, usuario)
            VALUES (%s,%s,%s,%s,%s)
            """, (produto, qtd, valor, fornecedor, session["user"]))

            conn.commit()
            registrar_log(session["user"], "entrada_produto", produto)

            msg = "✅ Entrada registrada"

        except Exception as e:
            conn.rollback()
            msg = f"❌ Erro: {e}"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>📥 ENTRADA DE PRODUTOS</h2>

    <form method="POST">
    <input name="produto" placeholder="Produto" required>
    <input name="qtd" placeholder="Quantidade" required>
    <input name="valor" placeholder="Valor (R$)" required>
    <input name="fornecedor" placeholder="Fornecedor" required>
    <button>Registrar</button>
    </form>

    <p>{msg}</p>
    </div>
    """)

# ================= TRANSFERENCIA =================
@estoque_bp.route("/transferencia", methods=["GET","POST"])
def transferencia():
    conn = conectar()
    cursor = conn.cursor()
    msg=""

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])

        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s",(produto,))
        dado = cursor.fetchone()

        if dado and dado[0] >= qtd:
            cursor.execute("UPDATE estoque SET quantidade=%s WHERE produto=%s",(dado[0]-qtd,produto))
            cursor.execute("INSERT INTO transferencias (produto,quantidade,origem,destino,usuario) VALUES (%s,%s,%s,%s,%s)",
            (produto,qtd,"estoque","saida",session["user"]))
            conn.commit()
            msg="✅ Transferido"
        else:
            msg="❌ Sem estoque"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>Transferência</h2>
    <form method="POST">
    <input name="produto">
    <input name="qtd">
    <button>Enviar</button>
    </form>
    <p>{msg}</p>
    </div>
    """)

# ================= HISTÓRICO COMPLETO =================
@estoque_bp.route("/historico", methods=["GET"])
def historico():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    produto = request.args.get("produto", "")
    usuario = request.args.get("usuario", "")
    data = request.args.get("data", "")

    filtro_sql = ""
    valores = []

    if produto:
        filtro_sql += " AND produto ILIKE %s"
        valores.append(f"%{produto}%")

    if usuario:
        filtro_sql += " AND usuario ILIKE %s"
        valores.append(f"%{usuario}%")

    if data:
        filtro_sql += " AND DATE(data) = %s"
        valores.append(data)

    cursor.execute(f"""
    SELECT produto, quantidade, 'TRANSFERÊNCIA', origem, destino, usuario, data FROM transferencias WHERE 1=1 {filtro_sql}
    UNION ALL
    SELECT produto, quantidade, 'ENTRADA', 'fornecedor', fornecedor, usuario, data FROM entradas WHERE 1=1 {filtro_sql}
    ORDER BY data DESC
    """, valores * 2)

    dados = cursor.fetchall()

    tabela = ""
    for p,q,tipo,o,d,u,data in dados:
        cor = "#00ff00" if tipo == "ENTRADA" else "#ff4444"
        tabela += f"""
        <tr>
        <td>{p}</td>
        <td>{q}</td>
        <td style="color:{cor}">{tipo}</td>
        <td>{o}</td>
        <td>{d}</td>
        <td>{u}</td>
        <td>{data}</td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>📊 HISTÓRICO</h2>

    <table>
    <tr>
    <th>Produto</th><th>Qtd</th><th>Tipo</th><th>Origem</th><th>Destino</th><th>User</th><th>Data</th>
    </tr>
    {tabela}
    </table>
    </div>
    """)
