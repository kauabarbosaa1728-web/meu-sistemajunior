from flask import Flask, render_template_string, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "segredo123"

ADMIN = "kaua.barbosa1728@gmail.com"

def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT UNIQUE,
        senha TEXT,
        online INTEGER DEFAULT 0,
        ultimo_login TIMESTAMP
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

def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE user=?", (ADMIN,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (user, senha) VALUES (?,?)",
                       (ADMIN, generate_password_hash("997401054")))
        conn.commit()

    conn.close()

criar_admin()

# LOGIN
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

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user

            cursor.execute("""
            UPDATE usuarios SET online=1, ultimo_login=CURRENT_TIMESTAMP WHERE user=?
            """, (user,))
            conn.commit()
            conn.close()

            return redirect("/sistema")
        else:
            erro = "Login inválido"
            conn.close()

    return f"""
    <html><head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="bg-dark d-flex justify-content-center align-items-center" style="height:100vh;">
    <div class="card p-4" style="width:350px;">
    <h3>🔐 KBSistemas</h3>
    <form method="POST">
    <input name="user" class="form-control mb-2" placeholder="Usuário">
    <input name="senha" type="password" class="form-control mb-3" placeholder="Senha">
    <button class="btn btn-primary w-100">Entrar</button>
    </form>
    <p class="text-danger">{erro}</p>
    </div>
    </body></html>
    """

# SISTEMA
@app.route("/sistema", methods=["GET","POST"])
def sistema():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    busca = request.args.get("busca", "")
    filtro = request.args.get("filtro", "")

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

    botao_admin = ""
    if session["user"] == ADMIN:
        botao_admin = '<li><a class="dropdown-item" href="/admin">Usuários</a></li>'

    return f"""
    <html><head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body>

    <nav class="navbar navbar-dark bg-dark">
    <div class="container-fluid">
    <span class="navbar-brand">📦 KBSistemas</span>

    <div class="dropdown">
    <button class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown">Menu</button>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="/sistema">Estoque</a></li>
        <li><a class="dropdown-item" href="/historico">Histórico</a></li>
        {botao_admin}
    </ul>
    </div>

    <a href="/logout" class="btn btn-danger">Sair</a>
    </div>
    </nav>

    <div class="container mt-4">

    <form method="GET" class="row mb-3">
        <input name="busca" class="form-control col" placeholder="Buscar">
    </form>

    <form method="POST" class="row mb-3">
        <input name="produto" class="form-control col" placeholder="Produto">
        <input name="qtd" type="number" class="form-control col" placeholder="Qtd">
        <select name="categoria" class="form-control col">
            <option>Eletrônicos</option>
            <option>Ferramentas</option>
            <option>Escritório</option>
        </select>
        <button class="btn btn-success col">Adicionar</button>
    </form>

    <table class="table table-striped">
    <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ações</th></tr>
    {tabela}
    </table>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body></html>
    """

# ADMIN
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "user" not in session or session["user"] != ADMIN:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        novo = request.form["novo"]
        senha = request.form["senha"]

        cursor.execute("INSERT INTO usuarios (user, senha) VALUES (?,?)",
                       (novo, generate_password_hash(senha)))
        conn.commit()

    cursor.execute("SELECT user, online, ultimo_login FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u, o, l in dados:
        status = "🟢" if o else "🔴"

        tabela += f"""
        <tr>
            <td>{u}</td>
            <td>{status}</td>
            <td>{l}</td>
            <td>
                <form action="/alterar/{u}" method="POST">
                    <input name="senha" placeholder="Nova senha">
                    <button class="btn btn-warning btn-sm">Alterar</button>
                </form>
            </td>
        </tr>
        """

    return f"""
    <html><head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-4">

    <h2>👑 Admin</h2>

    <form method="POST" class="mb-3">
        <input name="novo" placeholder="Novo usuário">
        <input name="senha" placeholder="Senha">
        <button class="btn btn-success">Criar</button>
    </form>

    <table class="table">
    <tr><th>Usuário</th><th>Status</th><th>Último Login</th><th>Ação</th></tr>
    {tabela}
    </table>

    <a href="/sistema" class="btn btn-secondary">Voltar</a>

    </body></html>
    """

@app.route("/alterar/<user>", methods=["POST"])
def alterar(user):
    conn = conectar()
    cursor = conn.cursor()

    senha = request.form["senha"]

    cursor.execute("UPDATE usuarios SET senha=? WHERE user=?",
                   (generate_password_hash(senha), user))

    conn.commit()
    conn.close()

    return redirect("/admin")

# LOGOUT
@app.route("/logout")
def logout():
    conn = conectar()
    cursor = conn.cursor()

    if "user" in session:
        cursor.execute("UPDATE usuarios SET online=0 WHERE user=?", (session["user"],))
        conn.commit()

    conn.close()
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
