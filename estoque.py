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
@estoque_bp.route("/editar_estoque/<int:id>", methods=["GET", "POST"])
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
        registrar_log(session["user"], "editar_estoque", produto)
        devolver_conexao(conn)
        return redirect("/estoque")

    cursor.execute("SELECT produto, quantidade, categoria FROM estoque WHERE id=%s", (id,))
    dado = cursor.fetchone()

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>✏️ EDITAR PRODUTO</h2>

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

    if not tem_permissao("pode_excluir_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM estoque WHERE id=%s", (id,))
        conn.commit()
        registrar_log(session["user"], "excluir_estoque", str(id))
    except Exception as e:
        conn.rollback()
        print("Erro ao excluir:", e)

    devolver_conexao(conn)
    return redirect("/estoque")

# ================= ENTRADA =================
@estoque_bp.route("/entrada", methods=["GET", "POST"])
def entrada():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    if request.method == "POST":
        try:
            produto = request.form.get("produto")
            qtd = int(request.form.get("qtd"))
            valor = float(request.form.get("valor").replace(",", "."))
            fornecedor = request.form.get("fornecedor")

            cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
            dado = cursor.fetchone()

            if dado:
                cursor.execute("UPDATE estoque SET quantidade=%s WHERE produto=%s",
                               (dado[0] + qtd, produto))
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
            msg = "✅ Entrada registrada"

        except Exception as e:
            conn.rollback()
            msg = f"❌ Erro: {e}"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>📥 ENTRADA DE PRODUTOS</h2>

    <form method="POST">
    <input name="produto" required>
    <input name="qtd" required>
    <input name="valor" required>
    <input name="fornecedor" required>
    <button>Registrar</button>
    </form>

    <p>{msg}</p>
    </div>
    """)

# ================= TRANSFERENCIA CORRIGIDA =================
@estoque_bp.route("/transferencia", methods=["GET","POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    msg=""

    # PRODUTOS
    cursor.execute("SELECT produto FROM estoque")
    produtos = [p[0] for p in cursor.fetchall()]

    # USUÁRIOS (CORRIGIDO)
    try:
        cursor.execute("SELECT usuario FROM usuarios")
        usuarios = [u[0] for u in cursor.fetchall()]
    except:
        usuarios = []

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])
        destino = request.form.get("destino")

        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s",(produto,))
        dado = cursor.fetchone()

        if dado and dado[0] >= qtd:
            try:
                cursor.execute(
                    "UPDATE estoque SET quantidade=%s WHERE produto=%s",
                    (dado[0] - qtd, produto)
                )

                cursor.execute("""
                INSERT INTO transferencias (produto,quantidade,origem,destino,usuario)
                VALUES (%s,%s,%s,%s,%s)
                """, (produto, qtd, "estoque", destino or "saida", session["user"]))

                conn.commit()
                registrar_log(session["user"], "transferencia", f"{produto} -> {destino}")

                msg="✅ Transferência realizada"
            except Exception as e:
                conn.rollback()
                msg=f"❌ Erro: {e}"
        else:
            msg="❌ Estoque insuficiente"

    # HISTÓRICO CORRIGIDO
    try:
        cursor.execute("""
        SELECT produto, quantidade, destino, usuario 
        FROM transferencias ORDER BY id DESC LIMIT 5
        """)
        historico = cursor.fetchall()
    except:
        historico = []

    lista_produtos = "".join([f"<option value='{p}'>{p}</option>" for p in produtos])
    lista_usuarios = "".join([f"<option value='{u}'>{u}</option>" for u in usuarios])

    tabela = ""
    for h in historico:
        p = h[0]
        q = h[1]
        d = h[2]
        u = h[3]

        tabela += f"""
        <tr>
        <td>{p}</td>
        <td>{q}</td>
        <td>{d}</td>
        <td>{u}</td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>🔁 TRANSFERÊNCIA</h2>

    <form method="POST" style="display:flex; gap:10px; flex-wrap:wrap;">
    
        <div>
        <label>📦 Produto</label><br>
        <select name="produto" required>
        {lista_produtos}
        </select>
        </div>

        <div>
        <label>🔢 Quantidade</label><br>
        <input name="qtd" type="number" required>
        </div>

        <div>
        <label>👤 Destino</label><br>
        <select name="destino">
        <option value="">Saída</option>
        {lista_usuarios}
        </select>
        </div>

        <div style="align-self:end;">
        <button>🚀 Transferir</button>
        </div>

    </form>

    <p>{msg}</p>

    <hr>

    <h3>📊 Últimas Transferências</h3>

    <table>
    <tr>
    <th>Produto</th><th>Qtd</th><th>Destino</th><th>Usuário</th>
    </tr>
    {tabela}
    </table>

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
    SELECT produto, quantidade, 'TRANSFERÊNCIA', origem, destino, usuario, data FROM transferencias
    UNION ALL
    SELECT produto, quantidade, 'ENTRADA', 'fornecedor', fornecedor, usuario, data FROM entradas
    ORDER BY data DESC
    """)

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
