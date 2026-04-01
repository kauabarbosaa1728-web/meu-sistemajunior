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
                cursor.execute("INSERT INTO estoque (produto, quantidade, categoria) VALUES (%s,%s,%s)", (produto, qtd, categoria))
                conn.commit()
                registrar_log(session["user"], "add_estoque", produto)
                msg = "✅ Adicionado"
            except:
                msg = "❌ Erro"
        else:
            msg = "❌ Preencha tudo"

    cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque ORDER BY id DESC")
    dados = cursor.fetchall()

    tabela = ""
    for i,p,q,c in dados:
        tabela += f"""
        <tr>
        <td>{i}</td><td>{p}</td><td>{q}</td><td>{c}</td>
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

    <form method="POST">
    <input name="produto" placeholder="Produto">
    <input name="qtd" placeholder="Qtd">
    <input name="categoria" placeholder="Categoria">
    <button>Adicionar</button>
    </form>

    <p>{msg}</p>

    <table>
    <tr><th>ID</th><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ações</th></tr>
    {tabela}
    </table>
    </div>
    """)

# ================= EDITAR =================
@estoque_bp.route("/editar_estoque/<int:id>", methods=["GET","POST"])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("UPDATE estoque SET produto=%s, quantidade=%s, categoria=%s WHERE id=%s",
        (request.form["produto"], request.form["qtd"], request.form["categoria"], id))
        conn.commit()
        devolver_conexao(conn)
        return redirect("/estoque")

    cursor.execute("SELECT produto, quantidade, categoria FROM estoque WHERE id=%s",(id,))
    p,q,c = cursor.fetchone()
    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>Editar</h2>
    <form method="POST">
    <input name="produto" value="{p}">
    <input name="qtd" value="{q}">
    <input name="categoria" value="{c}">
    <button>Salvar</button>
    </form>
    </div>
    """)

# ================= EXCLUIR =================
@estoque_bp.route("/excluir_estoque/<int:id>")
def excluir(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque WHERE id=%s",(id,))
    conn.commit()
    devolver_conexao(conn)
    return redirect("/estoque")

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

# ================= HISTÓRICO =================
@estoque_bp.route("/historico")
def historico():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto, quantidade, origem, destino, usuario, data FROM transferencias ORDER BY data DESC")
    dados = cursor.fetchall()

    tabela=""
    for d in dados:
        tabela+=f"<tr>{''.join(f'<td>{x}</td>' for x in d)}</tr>"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>Histórico</h2>

    <a href="/exportar_pdf">PDF</a>
    <a href="/exportar_excel">Excel</a>

    <table>
    <tr><th>Produto</th><th>Qtd</th><th>Origem</th><th>Destino</th><th>User</th><th>Data</th></tr>
    {tabela}
    </table>
    </div>
    """)

# ================= PDF =================
@estoque_bp.route("/exportar_pdf")
def pdf():
    conn=conectar()
    cursor=conn.cursor()
    cursor.execute("SELECT produto, quantidade, origem, destino, usuario, data FROM transferencias")
    dados=cursor.fetchall()

    doc=SimpleDocTemplate("historico.pdf", pagesize=letter)
    tabela=[["Produto","Qtd","Origem","Destino","User","Data"]]+[list(map(str,x)) for x in dados]
    t=Table(tabela)
    t.setStyle([('GRID',(0,0),(-1,-1),1,colors.black)])
    doc.build([t])

    devolver_conexao(conn)
    return redirect("/historico")

# ================= EXCEL =================
@estoque_bp.route("/exportar_excel")
def excel():
    conn=conectar()
    cursor=conn.cursor()
    cursor.execute("SELECT produto, quantidade, origem, destino, usuario, data FROM transferencias")
    dados=cursor.fetchall()

    wb=Workbook()
    ws=wb.active
    ws.append(["Produto","Qtd","Origem","Destino","User","Data"])
    for d in dados:
        ws.append(d)

    wb.save("historico.xlsx")

    devolver_conexao(conn)
    return redirect("/historico")
