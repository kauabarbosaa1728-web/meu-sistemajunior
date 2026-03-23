from flask import Flask, render_template_string, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "segredo123"

# CONEXÃO
def conectar():
    return sqlite3.connect("banco.db")

# CRIAR BANCO
def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT UNIQUE,
        senha TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT,
        quantidade INTEGER,
        tipo TEXT,
        usuario TEXT,
        categoria TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

criar_banco()

# CRIAR ADMIN
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE user=?", ("kaua.barbosa1728@gmail.com",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (user, senha) VALUES (?,?)",
                       ("kaua.barbosa1728@gmail.com", generate_password_hash("997401054")))
        conn.commit()

    conn.close()

criar_admin()

# LOGIN
html_login = """
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-dark d-flex justify-content-center align-items-center" style="height:100vh;">
<div class="card p-4" style="width:350px;">
<h3 class="text-center">🔐 KBSistemas</h3>

<form method="POST">
<input name="user" class="form-control mb-2" placeholder="Usuário">
<input name="senha" type="password" class="form-control mb-3" placeholder="Senha">
<button class="btn btn-primary w-100">Entrar</button>
</form>

<p class="text-danger">{{erro}}</p>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE user=?", (user,))
        dado = cursor.fetchone()
        conn.close()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            return redirect("/sistema")
        else:
            erro = "Login inválido"

    return render_template_string(html_login, erro=erro)

# SISTEMA
@app.route("/sistema", methods=["GET","POST"])
def sistema():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # FILTRO
    busca = request.args.get("busca", "")
    filtro = request.args.get("filtro", "")

    # ADICIONAR
    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])
        categoria = request.form["categoria"]

        cursor.execute("INSERT INTO estoque (produto, quantidade, categoria) VALUES (?,?,?)",
                       (produto, qtd, categoria))

        cursor.execute("""
        INSERT INTO movimentacoes (produto, quantidade, tipo, usuario, categoria)
        VALUES (?, ?, ?, ?, ?)
        """, (produto, qtd, "entrada", session["user"], categoria))

        conn.commit()

    # BUSCA + FILTRO
    query = "SELECT produto, quantidade, categoria FROM estoque WHERE 1=1"
    params = []

    if busca:
        query += " AND produto LIKE ?"
        params.append(f"%{busca}%")

    if filtro:
        query += " AND categoria=?"
        params.append(filtro)

    cursor.execute(query, params)
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    total = 0

    for p, q, c in dados:
        tabela += f"""
        <tr>
            <td>{p}</td>
            <td>{q}</td>
            <td>{c}</td>
            <td>
                <form action="/editar/{p}" method="POST" style="display:inline;">
                    <input name="qtd" type="number" value="{q}" style="width:80px;">
                    <button class="btn btn-primary btn-sm">Atualizar</button>
                </form>
                <a href="/deletar/{p}" class="btn btn-danger btn-sm">Excluir</a>
            </td>
        </tr>
        """
        total += q

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>KBSistemas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>

    <body>

    <!-- MENU -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <a class="navbar-brand">📦 KBSistemas</a>

        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto">

            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown">Estoque</a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="/sistema">Movimentações</a></li>
                <li><a class="dropdown-item" href="/historico">Histórico</a></li>
              </ul>
            </li>

          </ul>

          <a href="/logout" class="btn btn-danger">Sair</a>
        </div>
      </div>
    </nav>

    <div class="container mt-4">

    <!-- BUSCA -->
    <form method="GET" class="row mb-3">
        <div class="col-md-4">
            <input name="busca" class="form-control" placeholder="Buscar produto">
        </div>

        <div class="col-md-4">
            <select name="filtro" class="form-control">
                <option value="">Todas categorias</option>
                <option>Eletrônicos</option>
                <option>Ferramentas</option>
                <option>Escritório</option>
            </select>
        </div>

        <div class="col-md-2">
            <button class="btn btn-primary w-100">Filtrar</button>
        </div>
    </form>

    <!-- CARDS -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card p-3 text-center shadow">
                <h5>Total de Produtos</h5>
                <h2>{len(dados)}</h2>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card p-3 text-center shadow">
                <h5>Total em Estoque</h5>
                <h2>{total}</h2>
            </div>
        </div>
    </div>

    <!-- FORM -->
    <div class="card p-4 mb-4 shadow">
    <form method="POST" class="row g-3">
        <div class="col-md-4">
            <input name="produto" class="form-control" placeholder="Produto">
        </div>
        <div class="col-md-3">
            <input name="qtd" type="number" class="form-control" placeholder="Quantidade">
        </div>
        <div class="col-md-3">
            <select name="categoria" class="form-control">
                <option>Eletrônicos</option>
                <option>Ferramentas</option>
                <option>Escritório</option>
            </select>
        </div>
        <div class="col-md-2">
            <button class="btn btn-success w-100">Adicionar</button>
        </div>
    </form>
    </div>

    <!-- TABELA -->
    <div class="card p-4 shadow">
    <table class="table table-striped">
        <thead class="table-dark">
            <tr>
                <th>Produto</th>
                <th>Quantidade</th>
                <th>Categoria</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {tabela}
        </tbody>
    </table>
    </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    </body>
    </html>
    """

# EDITAR
@app.route("/editar/<produto>", methods=["POST"])
def editar(produto):
    nova_qtd = request.form["qtd"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE estoque SET quantidade=? WHERE produto=?", (nova_qtd, produto))

    cursor.execute("""
    INSERT INTO movimentacoes (produto, quantidade, tipo, usuario)
    VALUES (?, ?, ?, ?)
    """, (produto, nova_qtd, "edição", session["user"]))

    conn.commit()
    conn.close()

    return redirect("/sistema")

# DELETAR
@app.route("/deletar/<produto>")
def deletar(produto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM estoque WHERE produto=?", (produto,))

    cursor.execute("""
    INSERT INTO movimentacoes (produto, quantidade, tipo, usuario)
    VALUES (?, ?, ?, ?)
    """, (produto, 0, "exclusão", session["user"]))

    conn.commit()
    conn.close()

    return redirect("/sistema")

# HISTÓRICO
@app.route("/historico")
def historico():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto, quantidade, tipo, usuario, data FROM movimentacoes ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for p, q, t, u, d in dados:
        tabela += f"""
        <tr>
            <td>{p}</td>
            <td>{q}</td>
            <td>{t}</td>
            <td>{u}</td>
            <td>{d}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>

    <body class="bg-light">

    <div class="container mt-4">
        <h2>📊 Histórico de Movimentações</h2>

        <table class="table table-striped">
            <thead class="table-dark">
                <tr>
                    <th>Produto</th>
                    <th>Quantidade</th>
                    <th>Tipo</th>
                    <th>Usuário</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tbody>
                {tabela}
            </tbody>
        </table>

        <a href="/sistema" class="btn btn-secondary">Voltar</a>
    </div>

    </body>
    </html>
    """

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# RODAR
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
