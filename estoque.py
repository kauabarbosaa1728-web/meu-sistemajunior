from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao, registrar_log
from layout import container, acesso_negado, tem_permissao

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

    # ===== CADASTRAR =====
    if request.method == "POST":
        produto = request.form.get("produto", "").strip()
        qtd = request.form.get("qtd", "").strip()
        categoria = request.form.get("categoria", "").strip()

        if not produto or not qtd or not categoria:
            mensagem = "❌ Preencha todos os campos."
        else:
            try:
                qtd_int = int(qtd)

                if qtd_int < 0:
                    mensagem = "❌ Quantidade inválida."
                else:
                    cursor.execute("""
                    INSERT INTO estoque (produto, quantidade, categoria)
                    VALUES (%s, %s, %s)
                    """, (produto, qtd_int, categoria))
                    conn.commit()

                    registrar_log(session["user"], "add_estoque", f"{produto} ({qtd_int})")

                    mensagem = "✅ Produto adicionado com sucesso."

            except:
                mensagem = "❌ Erro na quantidade."

    # ===== BUSCA =====
    busca = request.args.get("busca", "").strip()

    if busca:
        cursor.execute("""
        SELECT id, produto, quantidade, categoria
        FROM estoque
        WHERE produto ILIKE %s OR categoria ILIKE %s
        ORDER BY id DESC
        """, (f"%{busca}%", f"%{busca}%"))
    else:
        cursor.execute("""
        SELECT id, produto, quantidade, categoria
        FROM estoque
        ORDER BY id DESC
        """)

    dados = cursor.fetchall()

    # ===== ALERTA =====
    alerta = ""
    for i, p, q, c in dados:
        if q <= 10:
            alerta += f"<p style='color:#ff4d4d;'>⚠ {p} com estoque baixo ({q})</p>"

    # ===== TABELA =====
    tabela = ""
    for i, p, q, c in dados:
        acoes = ""

        if tem_permissao("pode_editar_estoque"):
            acoes += f"<a href='/editar_estoque/{i}' class='btn-warning'>Editar</a> "

        if tem_permissao("pode_excluir_estoque"):
            acoes += f"<a href='/excluir_estoque/{i}' class='btn-danger'>Excluir</a>"

        if not acoes:
            acoes = "<span style='color:gray;'>Sem permissão</span>"

        tabela += f"""
        <tr>
            <td>{i}</td>
            <td>{p}</td>
            <td>{q}</td>
            <td>{c}</td>
            <td>{acoes}</td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
        <h2>📦 ESTOQUE PROFISSIONAL</h2>

        {alerta}

        <form method="POST">
            <input name="produto" placeholder="Produto" required>
            <input name="qtd" placeholder="Quantidade" required>
            <input name="categoria" placeholder="Categoria" required>
            <button>Adicionar</button>
        </form>

        <div class="mensagem">{mensagem}</div>
    </div>

    <div class="card">
        <form method="GET">
            <input name="busca" placeholder="Buscar produto ou categoria" value="{busca}">
            <button>Buscar</button>
            <a href="/estoque">Limpar</a>
        </form>

        <table>
            <tr>
                <th>ID</th>
                <th>Produto</th>
                <th>Qtd</th>
                <th>Categoria</th>
                <th>Ações</th>
            </tr>
            {tabela}
        </table>
    </div>
    """)

# ================= EDITAR =================
@estoque_bp.route("/editar_estoque/<int:id>", methods=["GET", "POST"])
def editar(id):
    if not tem_permissao("pode_editar_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto, quantidade, categoria FROM estoque WHERE id=%s", (id,))
    dado = cursor.fetchone()

    if not dado:
        return "Item não encontrado"

    produto, qtd, categoria = dado

    if request.method == "POST":
        novo_produto = request.form["produto"]
        nova_qtd = int(request.form["qtd"])
        nova_categoria = request.form["categoria"]

        cursor.execute("""
        UPDATE estoque
        SET produto=%s, quantidade=%s, categoria=%s
        WHERE id=%s
        """, (novo_produto, nova_qtd, nova_categoria, id))

        conn.commit()

        registrar_log(session["user"], "edit_estoque", f"{id}")

        devolver_conexao(conn)
        return redirect("/estoque")

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
        <h2>✏️ Editar</h2>
        <form method="POST">
            <input name="produto" value="{produto}">
            <input name="qtd" value="{qtd}">
            <input name="categoria" value="{categoria}">
            <button>Salvar</button>
        </form>
    </div>
    """)

# ================= EXCLUIR =================
@estoque_bp.route("/excluir_estoque/<int:id>")
def excluir(id):
    if not tem_permissao("pode_excluir_estoque"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM estoque WHERE id=%s", (id,))
    conn.commit()

    registrar_log(session["user"], "delete_estoque", str(id))

    devolver_conexao(conn)
    return redirect("/estoque")

# ================= TRANSFERÊNCIA =================
@estoque_bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    if not tem_permissao("pode_transferencia"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()
    mensagem = ""

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])

        cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
        dado = cursor.fetchone()

        if dado and dado[0] >= qtd:
            nova = dado[0] - qtd

            cursor.execute("UPDATE estoque SET quantidade=%s WHERE produto=%s", (nova, produto))

            cursor.execute("""
            INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
            VALUES (%s,%s,%s,%s,%s)
            """, (produto, qtd, "estoque", "saida", session["user"]))

            conn.commit()

            registrar_log(session["user"], "transferencia", produto)

            mensagem = "✅ Transferência realizada"
        else:
            mensagem = "❌ Estoque insuficiente"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
        <h2>🔄 Transferência</h2>

        <form method="POST">
            <input name="produto" placeholder="Produto">
            <input name="qtd" placeholder="Quantidade">
            <button>Transferir</button>
        </form>

        <p>{mensagem}</p>
    </div>
    """)

# ================= LOGS =================
@estoque_bp.route("/logs")
def logs():
    if not tem_permissao("pode_logs"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT usuario, acao, detalhes, data FROM logs ORDER BY id DESC LIMIT 100")
    dados = cursor.fetchall()

    tabela = ""
    for u, a, d, dt in dados:
        tabela += f"<tr><td>{u}</td><td>{a}</td><td>{d}</td><td>{dt}</td></tr>"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
        <h2>📋 LOGS</h2>

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
    """)
    # ================= HISTÓRICO =================
@estoque_bp.route("/historico")
def historico():
    if not tem_permissao("pode_historico"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT produto, quantidade, origem, destino, usuario, data
    FROM transferencias
    ORDER BY id DESC
    LIMIT 100
    """)

    dados = cursor.fetchall()

    tabela = ""
    for p, q, o, d, u, dt in dados:
        tabela += f"""
        <tr>
            <td>{p}</td>
            <td>{q}</td>
            <td>{o}</td>
            <td>{d}</td>
            <td>{u}</td>
            <td>{dt}</td>
        </tr>
        """

    if not tabela:
        tabela = "<tr><td colspan='6'>Sem histórico ainda</td></tr>"

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
        <h2>📜 HISTÓRICO DE TRANSFERÊNCIAS</h2>

        <table>
            <tr>
                <th>Produto</th>
                <th>Qtd</th>
                <th>Origem</th>
                <th>Destino</th>
                <th>Usuário</th>
                <th>Data</th>
            </tr>
            {tabela}
        </table>
    </div>
    """)
