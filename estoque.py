from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao, registrar_log
from layout import container, acesso_negado, tem_permissao

estoque_bp = Blueprint("estoque_bp", **name**)

# ================= ESTOQUE =================

@estoque_bp.route("/estoque", methods=["GET", "POST"])
def estoque():
if "user" not in session:
return redirect("/")

```
if not tem_permissao("pode_estoque"):
    return acesso_negado()

conn = conectar()
cursor = conn.cursor()
mensagem = ""

# ===== CADASTRAR =====
if request.method == "POST":
    produto = request.form["produto"].strip()
    qtd = request.form["qtd"].strip()
    categoria = request.form["categoria"].strip()

    try:
        qtd_int = int(qtd)

        if qtd_int < 0:
            mensagem = "Quantidade inválida."
        else:
            cursor.execute("""
            INSERT INTO estoque (produto, quantidade, categoria)
            VALUES (%s, %s, %s)
            """, (produto, qtd_int, categoria))
            conn.commit()

            registrar_log(session["user"], "add_estoque", produto)

            mensagem = "Produto adicionado com sucesso."

    except:
        mensagem = "Erro ao cadastrar."

# ===== BUSCA =====
busca = request.args.get("busca", "")

if busca:
    cursor.execute("""
    SELECT * FROM estoque WHERE produto ILIKE %s
    """, (f"%{busca}%",))
else:
    cursor.execute("SELECT * FROM estoque")

dados = cursor.fetchall()

# ===== ALERTA =====
alerta = ""
for item in dados:
    if item[2] <= 10:
        alerta += f"<p style='color:red;'>⚠ {item[1]} com estoque baixo ({item[2]})</p>"

tabela = ""
for item in dados:
    acoes = ""

    if tem_permissao("pode_editar_estoque"):
        acoes += f"<a href='/editar_estoque/{item[0]}'>Editar</a> "

    if tem_permissao("pode_excluir_estoque"):
        acoes += f"<a href='/excluir_estoque/{item[0]}'>Excluir</a>"

    tabela += f"""
    <tr>
        <td>{item[1]}</td>
        <td>{item[2]}</td>
        <td>{item[3]}</td>
        <td>{acoes}</td>
    </tr>
    """

devolver_conexao(conn)

return container(f"""
<div class="card">
    <h2>📦 ESTOQUE</h2>

    {alerta}

    <form method="POST">
        <input name="produto" placeholder="Produto" required>
        <input name="qtd" placeholder="Quantidade" required>
        <input name="categoria" placeholder="Categoria" required>
        <button>Adicionar</button>
    </form>

    <p>{mensagem}</p>
</div>

<div class="card">
    <form method="GET">
        <input name="busca" placeholder="Buscar produto">
        <button>Buscar</button>
    </form>

    <table>
        <tr>
            <th>Produto</th>
            <th>Qtd</th>
            <th>Categoria</th>
            <th>Ações</th>
        </tr>
        {tabela}
    </table>
</div>
""")
```

# ================= EXCLUIR =================

@estoque_bp.route("/excluir_estoque/[int:id](int:id)")
def excluir(id):
if not tem_permissao("pode_excluir_estoque"):
return acesso_negado()

```
conn = conectar()
cursor = conn.cursor()

cursor.execute("DELETE FROM estoque WHERE id=%s", (id,))
conn.commit()

registrar_log(session["user"], "delete_estoque", str(id))

devolver_conexao(conn)
return redirect("/estoque")
```

# ================= TRANSFERÊNCIA =================

@estoque_bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
if not tem_permissao("pode_transferencia"):
return acesso_negado()

```
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
        conn.commit()

        registrar_log(session["user"], "transferencia", produto)

        mensagem = "Transferência feita"
    else:
        mensagem = "Erro na transferência"

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
```

# ================= LOGS =================

@estoque_bp.route("/logs")
def logs():
if not tem_permissao("pode_logs"):
return acesso_negado()

```
conn = conectar()
cursor = conn.cursor()

cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 100")
dados = cursor.fetchall()

tabela = ""
for l in dados:
    tabela += f"<tr><td>{l[1]}</td><td>{l[2]}</td><td>{l[3]}</td></tr>"

devolver_conexao(conn)

return container(f"""
<div class="card">
    <h2>📋 LOGS</h2>

    <table>
        <tr>
            <th>Usuário</th>
            <th>Ação</th>
            <th>Detalhes</th>
        </tr>
        {tabela}
    </table>
</div>
""")
```
