from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao, registrar_log
from layout import container, acesso_negado, tem_permissao

# PDF + EXCEL
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
    mensagem = ""

    if request.method == "POST":
        produto = request.form.get("produto", "").strip()
        qtd = request.form.get("qtd", "").strip()
        categoria = request.form.get("categoria", "").strip()

        if produto and qtd and categoria:
            try:
                qtd = int(qtd)
                cursor.execute("INSERT INTO estoque (produto, quantidade, categoria) VALUES (%s,%s,%s)", (produto, qtd, categoria))
                conn.commit()
                registrar_log(session["user"], "add_estoque", produto)
                mensagem = "✅ Adicionado"
            except:
                mensagem = "❌ Erro"
        else:
            mensagem = "❌ Preencha tudo"

    busca = request.args.get("busca", "")

    if busca:
        cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque WHERE produto ILIKE %s", (f"%{busca}%",))
    else:
        cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque")

    dados = cursor.fetchall()

    tabela = ""
    for i, p, q, c in dados:
        tabela += f"<tr><td>{i}</td><td>{p}</td><td>{q}</td><td>{c}</td></tr>"

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

    <p>{mensagem}</p>

    <form>
    <input name="busca" placeholder="Buscar">
    <button>Buscar</button>
    </form>

    <table>
    <tr><th>ID</th><th>Produto</th><th>Qtd</th><th>Categoria</th></tr>
    {tabela}
    </table>
    </div>
    """)

# ================= HISTÓRICO =================
@estoque_bp.route("/historico")
def historico():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto, quantidade, origem, destino, usuario, data FROM transferencias ORDER BY data DESC")
    dados = cursor.fetchall()

    tabela = ""
    for p,q,o,d,u,dt in dados:
        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{o}</td><td>{d}</td><td>{u}</td><td>{dt}</td></tr>"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>📜 HISTÓRICO</h2>

    <a href="/exportar_pdf">📄 PDF</a>
    <a href="/exportar_excel">📊 Excel</a>

    <table>
    <tr><th>Produto</th><th>Qtd</th><th>Origem</th><th>Destino</th><th>User</th><th>Data</th></tr>
    {tabela}
    </table>
    </div>
    """)

# ================= PDF =================
@estoque_bp.route("/exportar_pdf")
def exportar_pdf():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto, quantidade, origem, destino, usuario, data FROM transferencias")
    dados = cursor.fetchall()

    doc = SimpleDocTemplate("historico.pdf", pagesize=letter)

    tabela = [["Produto","Qtd","Origem","Destino","User","Data"]]
    for d in dados:
        tabela.append([str(x) for x in d])

    t = Table(tabela)
    t.setStyle([('GRID',(0,0),(-1,-1),1,colors.black)])

    doc.build([t])
    devolver_conexao(conn)

    return redirect("/historico")

# ================= EXCEL =================
@estoque_bp.route("/exportar_excel")
def exportar_excel():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto, quantidade, origem, destino, usuario, data FROM transferencias")
    dados = cursor.fetchall()

    wb = Workbook()
    ws = wb.active

    ws.append(["Produto","Qtd","Origem","Destino","User","Data"])

    for d in dados:
        ws.append(d)

    wb.save("historico.xlsx")
    devolver_conexao(conn)

    return redirect("/historico")
