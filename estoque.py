from flask import Blueprint, request, redirect, session, send_file
from banco import conectar, devolver_conexao, registrar_log, verificar_pagamento
from layout import container, acesso_negado
from permissoes import tem_permissao
from openpyxl import Workbook
from io import BytesIO

estoque_bp = Blueprint("estoque_bp", __name__)

# ================= ESTOQUE =================
@estoque_bp.route("/estoque", methods=["GET", "POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    aviso = ""

    if session.get("cargo") != "admin":
        status = verificar_pagamento(session["user"])

        if status == "bloqueado":
            return """
            <h1 style='color:red;text-align:center;margin-top:50px;'>
            🚫 Sistema bloqueado<br><br>
            Efetue o pagamento para continuar
            </h1>
            """

        elif status == "aviso":
            aviso = "<div style='color:yellow;text-align:center;'>⚠️ Seu plano está vencendo!</div>"

    if not tem_permissao("pode_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    # ================= ADICIONAR =================
    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")
        valor = request.form.get("valor")

        if produto and qtd:
            try:
                qtd = int(qtd)
                valor = float(valor or 0)

                cursor.execute("""
                INSERT INTO estoque (produto, quantidade, categoria, valor)
                VALUES (%s,%s,%s,%s)
                """, (produto, qtd, categoria, valor))

                conn.commit()
                registrar_log(session["user"], "add_estoque", f"{produto} ({qtd})")

                msg = "✅ Produto adicionado com sucesso"

            except Exception as e:
                conn.rollback()
                msg = f"❌ Erro: {e}"

    # ================= LISTAGEM =================
    cursor.execute("""
    SELECT id, produto, quantidade, categoria, valor 
    FROM estoque 
    ORDER BY id DESC
    """)
    dados = cursor.fetchall()

    total_qtd = sum([d[2] for d in dados])
    total_valor = sum([d[2] * float(d[4] or 0) for d in dados])

    # ================= ALERTA ESTOQUE BAIXO =================
    cursor.execute("""
    SELECT produto, quantidade 
    FROM estoque 
    WHERE quantidade <= 10
    ORDER BY quantidade ASC
    LIMIT 5
    """)
    baixo = cursor.fetchall()

    alerta_html = ""
    if baixo:
        alerta_html += "<div style='background:#330000;padding:10px;border-radius:8px;margin-bottom:15px;'>"
        alerta_html += "<b>⚠️ Estoque baixo:</b><br>"
        for p, q in baixo:
            alerta_html += f"<span style='color:red'>{p} - {q} unidades</span><br>"
        alerta_html += "</div>"

    # ================= TABELA =================
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
        <a href='/editar_estoque/{i}'>✏️</a>
        <a href='/excluir_estoque/{i}' onclick="return confirm('Tem certeza?')">🗑️</a>
        </td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    {aviso}
    {alerta_html}

    <h2>📦 ESTOQUE</h2>

    <!-- BOTÃO EXCEL -->
    <a href="/exportar_estoque" style="
    background:#16a34a;
    padding:10px;
    border-radius:6px;
    color:white;
    text-decoration:none;
    display:inline-block;
    margin-bottom:15px;
    ">
    📥 Exportar Excel
    </a>

    <!-- RESUMO -->
    <div style="background:#111;padding:15px;border-radius:8px;margin-bottom:20px;">
        <b>Quantidade total:</b> {total_qtd} <br>
        <b>Valor total:</b> R$ {total_valor:,.2f}
    </div>

    <div class="grid">

        <!-- FORM -->
        <div class="box">
            <h3>➕ Novo Produto</h3>

            <form method="POST">
                <input name="produto" placeholder="Produto" required>
                <input name="qtd" placeholder="Quantidade" required>
                <input name="categoria" placeholder="Categoria">
                <input name="valor" placeholder="Valor (R$)">
                <button>Adicionar</button>
            </form>

            <p>{msg}</p>
        </div>

        <!-- TABELA -->
        <div class="box">
            <h3>📋 Produtos</h3>

            <table>
            <tr>
            <th>ID</th>
            <th>Produto</th>
            <th>Qtd</th>
            <th>Categoria</th>
            <th>Valor</th>
            <th></th>
            </tr>
            {tabela}
            </table>
        </div>

    </div>

    <style>
    .grid {{
        display:grid;
        grid-template-columns:320px 1fr;
        gap:20px;
    }}

    input {{
        width:100%;
        padding:10px;
        margin-bottom:10px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    button {{
        width:100%;
        padding:10px;
        background:#3b82f6;
        border:none;
        border-radius:6px;
        color:white;
        cursor:pointer;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
    }}

    th {{
        background:#1a1a1a;
        padding:10px;
        text-align:left;
    }}

    td {{
        padding:10px;
        border-top:1px solid #333;
    }}

    tr:hover {{
        background:#111;
    }}
    </style>
    """)


# ================= EXPORTAR EXCEL =================
@estoque_bp.route("/exportar_estoque")
def exportar_estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT produto, quantidade, categoria, valor 
    FROM estoque
    """)
    dados = cursor.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Estoque"

    ws.append(["Produto", "Quantidade", "Categoria", "Valor Unitário", "Valor Total"])

    total_geral = 0

    for p, q, c, v in dados:
        valor_total = q * float(v or 0)
        total_geral += valor_total
        ws.append([p, q, c, float(v or 0), valor_total])

    ws.append([])
    ws.append(["", "", "", "TOTAL:", total_geral])

    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)

    devolver_conexao(conn)

    return send_file(
        arquivo,
        as_attachment=True,
        download_name="estoque.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ================= EDITAR =================
# ================= EDITAR =================
@estoque_bp.route("/editar_estoque/<int:id>", methods=["GET", "POST"])
def editar_estoque(id):
    if "user" not in session:
        return redirect("/")

    status = verificar_pagamento(session["user"])

    # 🔥 LIBERA ADMIN
    if status == "bloqueado" and session.get("cargo") != "admin":
        return "<h1 style='color:red'>🚫 Sistema bloqueado</h1>"

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")
        valor = request.form.get("valor")  # 🔥 NOVO

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

    # 🔥 AGORA BUSCA VALOR TAMBÉM
    cursor.execute("SELECT produto, quantidade, categoria, valor FROM estoque WHERE id=%s", (id,))
    dado = cursor.fetchone()

    devolver_conexao(conn)

    if not dado:
        return container("""
        <div class="card">
        <h2 style='color:red'>❌ Produto não encontrado</h2>
        <a href="/estoque">⬅ Voltar</a>
        </div>
        """)

    return container(f"""
    <div class="card">
    <h2>✏️ EDITAR PRODUTO</h2>

    <form method="POST" style="display:flex; gap:10px; flex-wrap:wrap;">
        <input name="produto" value="{dado[0]}" placeholder="Produto">
        <input name="qtd" value="{dado[1]}" placeholder="Quantidade">
        <input name="categoria" value="{dado[2]}" placeholder="Categoria">
        <input name="valor" value="{float(dado[3] or 0):.2f}" placeholder="Valor (R$)"> <!-- 🔥 NOVO -->
        <button>Salvar</button>
    </form>
    </div>
    """)

    if "user" not in session:
        return redirect("/")

    status = verificar_pagamento(session["user"])

    # 🔥 CORREÇÃO AQUI (libera admin)
    if status == "bloqueado" and session.get("cargo") != "admin":
        return "<h1 style='color:red'>🚫 Sistema bloqueado</h1>"

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")

        try:
            qtd = int(qtd)

            cursor.execute("""
            UPDATE estoque SET produto=%s, quantidade=%s, categoria=%s
            WHERE id=%s
            """, (produto, qtd, categoria, id))

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

    cursor.execute("SELECT produto, quantidade, categoria FROM estoque WHERE id=%s", (id,))
    dado = cursor.fetchone()

    devolver_conexao(conn)

    # 🔥 proteção caso não encontre o produto
    if not dado:
        return container("""
        <div class="card">
        <h2 style='color:red'>❌ Produto não encontrado</h2>
        <a href="/estoque">⬅ Voltar</a>
        </div>
        """)

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

    # 🔥 NÃO BLOQUEIA ADMIN
    if session.get("cargo") != "admin":
        status = verificar_pagamento(session["user"])

        if status == "bloqueado":
            return "<h1 style='color:red'>🚫 Sistema bloqueado</h1>"

    # 🔒 PERMISSÃO
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

    try:
        cursor.execute("SELECT usuario FROM usuarios")
        usuarios = [u[0] for u in cursor.fetchall()]
    except:
        usuarios = []

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])
        destino = request.form.get("destino")

        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
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

                msg = "✅ Transferência realizada"
            except Exception as e:
                conn.rollback()
                msg = f"❌ Erro: {e}"
        else:
            msg = "❌ Estoque insuficiente"

    # 🔥 AGORA COM DATA
    try:
        cursor.execute("""
        SELECT produto, quantidade, destino, usuario, data
        FROM transferencias 
        ORDER BY id DESC 
        LIMIT 10
        """)
        historico = cursor.fetchall()
    except:
        historico = []

    lista_produtos = "".join([f"<option value='{p}'>{p}</option>" for p in produtos])
    lista_usuarios = "".join([f"<option value='{u}'>{u}</option>" for u in usuarios])

    tabela = ""
    for h in historico:
        data_formatada = h[4].strftime("%d/%m/%Y %H:%M") if h[4] else "-"
        tabela += f"""
        <tr>
        <td>{h[0]}</td>
        <td>{h[1]}</td>
        <td>{h[2]}</td>
        <td>{h[3]}</td>
        <td>{data_formatada}</td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    <div class="wrap">

        <h2 style="margin-bottom:20px;">🔄 Transferência</h2>

        <div class="grid">

            <!-- FORM -->
            <div class="box">
                <h3>Nova Transferência</h3>

                <form method="POST">

                    <label>Produto</label>
                    <select name="produto" required>
                        {lista_produtos}
                    </select>

                    <label>Quantidade</label>
                    <input name="qtd" type="number" min="1" required>

                    <label>Destino</label>
                    <select name="destino" required>
                        <option value="saida">Saída</option>
                        <option value="lixo">Lixo</option>
                        {lista_usuarios}
                    </select>

                    <button>🚀 Transferir</button>
                </form>

                <p>{msg}</p>
            </div>

            <!-- HISTÓRICO -->
            <div class="box">
                <h3>📜 Histórico</h3>

                <table>
                    <tr>
                        <th>Produto</th>
                        <th>Qtd</th>
                        <th>Destino</th>
                        <th>Usuário</th>
                        <th>Data</th>
                    </tr>
                    {tabela}
                </table>
            </div>

        </div>

    </div>

    <style>

    .wrap {{
        max-width: 1300px;
        margin: auto;
    }}

    .grid {{
        display:grid;
        grid-template-columns:320px 1fr;
        gap:20px;
    }}

    .box {{
        background:#0b0b0b;
        border:1px solid #2c2c2c;
        padding:20px;
        border-radius:10px;
    }}

    label {{
        display:block;
        margin-top:10px;
        font-size:13px;
        color:#aaa;
    }}

    input, select {{
        width:100%;
        padding:10px;
        margin-top:5px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    button {{
        margin-top:15px;
        width:100%;
        padding:10px;
        background:#3b82f6;
        border:none;
        border-radius:6px;
        color:white;
        cursor:pointer;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
        margin-top:10px;
    }}

    th {{
        background:#1a1a1a;
        padding:10px;
        text-align:left;
    }}

    td {{
        padding:10px;
        border-top:1px solid #333;
    }}

    tr:hover {{
        background:#111;
    }}

    </style>
    """)
# ================= HISTÓRICO =================
@estoque_bp.route("/historico")
def historico():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    busca = request.args.get("busca", "")

    # 🔥 LOGS COMPLETOS
    cursor.execute(f"""
    SELECT usuario, acao, detalhes, data
    FROM logs
    WHERE usuario ILIKE %s OR acao ILIKE %s OR detalhes ILIKE %s
    ORDER BY data DESC
    LIMIT 100
    """, (f"%{busca}%", f"%{busca}%", f"%{busca}%"))

    dados = cursor.fetchall()

    tabela = ""
    for u, acao, det, data in dados:
        tabela += f"""
        <tr>
            <td>{u}</td>
            <td>{acao}</td>
            <td>{det}</td>
            <td>{data.strftime("%d/%m/%Y %H:%M:%S")}</td>
        </tr>
        """

    if not tabela:
        tabela = "<tr><td colspan='4'>Nenhum registro encontrado</td></tr>"

    devolver_conexao(conn)

    return container(f"""
    <h2 style="margin-bottom:20px;">📜 Histórico do Sistema</h2>

    <!-- BUSCA -->
    <form method="GET" style="margin-bottom:20px;">
        <input name="busca" placeholder="Buscar usuário, ação..." value="{busca}">
        <button>Buscar</button>
    </form>

    <!-- TABELA -->
    <div class="box">
        <table>
            <tr>
                <th>Usuário</th>
                <th>Ação</th>
                <th>Detalhes</th>
                <th>Data</th>
            </tr>
            {tabela}
        </table>
    </div>

    <style>

    input {{
        padding:10px;
        width:300px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    button {{
        padding:10px;
        background:#3b82f6;
        border:none;
        color:white;
        border-radius:6px;
        cursor:pointer;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
        font-size:14px;
    }}

    th {{
        background:#1a1a1a;
        padding:10px;
        text-align:left;
    }}

    td {{
        padding:10px;
        border-top:1px solid #333;
    }}

    tr:hover {{
        background:#111;
    }}

    </style>
    """)
# ================= ENTRADA DE PRODUTOS =================
@estoque_bp.route("/entrada", methods=["GET", "POST"])
def entrada():
    if "user" not in session:
        return redirect("/")

    # 🔥 BLOQUEIO DE PAGAMENTO
    status = verificar_pagamento(session["user"])

    if session.get("cargo") != "admin":
        if status == "bloqueado":
            return """
            <h1 style='color:red;text-align:center;margin-top:50px;'>
            🚫 Sistema bloqueado<br><br>
            Efetue o pagamento para continuar
            </h1>
            """

    if not tem_permissao("pode_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    # 🔥 CRIA TABELA DE HISTÓRICO SE NÃO EXISTIR
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entradas (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INT,
        categoria TEXT,
        fornecedor TEXT,
        valor NUMERIC,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

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

                # 🔥 adiciona no estoque
                cursor.execute("""
                INSERT INTO estoque (produto, quantidade, categoria, valor)
                VALUES (%s,%s,%s,%s)
                """, (produto, qtd, categoria, valor))

                # 🔥 salva no histórico
                cursor.execute("""
                INSERT INTO entradas (produto, quantidade, categoria, fornecedor, valor, usuario)
                VALUES (%s,%s,%s,%s,%s,%s)
                """, (produto, qtd, categoria, fornecedor, valor, session["user"]))

                conn.commit()
                registrar_log(session["user"], "entrada_estoque", produto)

                msg = "✅ Produto adicionado com sucesso"

            except Exception as e:
                conn.rollback()
                msg = f"❌ Erro: {e}"

    # 🔥 HISTÓRICO
    cursor.execute("""
    SELECT produto, quantidade, fornecedor, valor, usuario, data
    FROM entradas
    ORDER BY id DESC LIMIT 10
    """)
    historico = cursor.fetchall()

    tabela = ""
    for h in historico:
        tabela += f"""
        <tr>
        <td>{h[0]}</td>
        <td>{h[1]}</td>
        <td>{h[2]}</td>
        <td>R$ {float(h[3] or 0):,.2f}</td>
        <td>{h[4]}</td>
        <td>{h[5]}</td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>➕ ENTRADA DE PRODUTOS</h2>

    <form method="POST" style="display:flex; flex-direction:column; gap:10px;">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="categoria" placeholder="Categoria">
        <input name="fornecedor" placeholder="Fornecedor">
        <input name="valor" placeholder="Valor (R$)">
        <button>Adicionar</button>
    </form>

    <p>{msg}</p>

    <a href="/estoque">⬅ Voltar para estoque</a>
    </div>

    <div class="card">
    <h2>📊 HISTÓRICO DE ENTRADAS</h2>

    <table>
    <tr>
    <th>Produto</th><th>Qtd</th><th>Fornecedor</th><th>Valor</th><th>User</th><th>Data</th>
    </tr>
    {tabela}
    </table>
    </div>
    """)
