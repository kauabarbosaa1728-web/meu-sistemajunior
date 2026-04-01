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
            except Exception as e:
                msg = f"❌ Erro: {e}"
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

    <a href="/entrada">➕ Entrada de Produtos</a>

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

# ================= ENTRADA DE PRODUTOS =================
@estoque_bp.route("/entrada", methods=["GET", "POST"])
def entrada():
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
        valor = request.form.get("valor")
        fornecedor = request.form.get("fornecedor")

        try:
            qtd = int(qtd)
            valor = float(valor)

            cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
            dado = cursor.fetchone()

            if dado:
                nova_qtd = dado[0] + qtd
                cursor.execute("UPDATE estoque SET quantidade=%s WHERE produto=%s", (nova_qtd, produto))
            else:
                cursor.execute("INSERT INTO estoque (produto, quantidade, categoria) VALUES (%s,%s,%s)", (produto, qtd, "entrada"))

            cursor.execute("""
            INSERT INTO entradas (produto, quantidade, valor, fornecedor, usuario)
            VALUES (%s,%s,%s,%s,%s)
            """, (produto, qtd, valor, fornecedor, session["user"]))

            conn.commit()
            registrar_log(session["user"], "entrada_produto", f"{produto} +{qtd}")

            msg = "✅ Entrada registrada com sucesso"

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
            <input name="valor" placeholder="Valor unitário (R$)" required>
            <input name="fornecedor" placeholder="Fornecedor / Loja" required>
            <button>Registrar Entrada</button>
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

# ================= HISTÓRICO =================
@estoque_bp.route("/historico", methods=["GET"])
def historico():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # ================= FILTROS =================
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

    # ================= CONSULTA UNIFICADA =================
    cursor.execute(f"""
    SELECT produto, quantidade, 'TRANSFERÊNCIA' AS tipo, origem, destino, usuario, data
    FROM transferencias
    WHERE 1=1 {filtro_sql}

    UNION ALL

    SELECT produto, quantidade, 'ENTRADA' AS tipo, 'fornecedor', fornecedor, usuario, data
    FROM entradas
    WHERE 1=1 {filtro_sql}

    ORDER BY data DESC
    """, valores * 2)  # duplicado por causa do UNION

    dados = cursor.fetchall()

    tabela = ""
    total = 0

    for produto, qtd, tipo, origem, destino, user, data in dados:
        cor = "#00ff00" if tipo == "ENTRADA" else "#ff4444"

        tabela += f"""
        <tr>
            <td>{produto}</td>
            <td>{qtd}</td>
            <td style="color:{cor}; font-weight:bold;">{tipo}</td>
            <td>{origem}</td>
            <td>{destino}</td>
            <td>{user}</td>
            <td>{data}</td>
        </tr>
        """
        total += 1

    if not tabela:
        tabela = "<tr><td colspan='7'>Nenhum registro encontrado</td></tr>"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
        <h2>📊 HISTÓRICO COMPLETO</h2>

        <form method="GET" style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:15px;">
            <input name="produto" placeholder="Produto" value="{produto}">
            <input name="usuario" placeholder="Usuário" value="{usuario}">
            <input name="data" type="date" value="{data}">
            <button>Filtrar</button>
        </form>

        <div style="display:flex; gap:10px; margin-bottom:15px;">
            <a href="/exportar_pdf">📄 PDF</a>
            <a href="/exportar_excel">📊 Excel</a>
            <span style="margin-left:auto;">Total: <b>{total}</b></span>
        </div>

        <table style="width:100%; border-collapse: collapse;">
            <tr style="background:#222;">
                <th>Produto</th>
                <th>Qtd</th>
                <th>Tipo</th>
                <th>Origem</th>
                <th>Destino</th>
                <th>Usuário</th>
                <th>Data</th>
            </tr>
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
