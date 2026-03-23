from flask import Flask, render_template_string, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "segredo123"

# CONEXÃO COM BANCO
def conectar():
    return sqlite3.connect("banco.db")

# CRIAR TABELAS
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
        quantidade INTEGER
    )
    """)

    conn.commit()
    conn.close()

criar_banco()

# CRIAR ADMIN SE NÃO EXISTIR
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

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])

        cursor.execute("INSERT INTO estoque (produto, quantidade) VALUES (?,?)", (produto, qtd))
        conn.commit()

    cursor.execute("SELECT produto, quantidade FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    total = 0

    for p, q in dados:
        tabela += f"<tr><td>{p}</td><td>{q}</td></tr>"
        total += q

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>Painel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>

    <body>

    <nav class="navbar navbar-dark bg-dark px-4">
        <span class="navbar-brand">KBSistemas</span>
        <a href="/logout" class="btn btn-danger">Sair</a>
    </nav>

    <div class="container mt-4">

    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card p-3 text-center shadow">
                <h5>Produtos</h5>
                <h2>{len(dados)}</h2>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card p-3 text-center shadow">
                <h5>Total</h5>
                <h2>{total}</h2>
            </div>
        </div>
    </div>

    <div class="card p-4 mb-4 shadow">
    <form method="POST" class="row g-3">
        <div class="col-md-6">
            <input name="produto" class="form-control" placeholder="Produto">
        </div>
        <div class="col-md-4">
            <input name="qtd" type="number" class="form-control" placeholder="Quantidade">
        </div>
        <div class="col-md-2">
            <button class="btn btn-success w-100">Adicionar</button>
        </div>
    </form>
    </div>

    <div class="card p-4 shadow">
    <table class="table table-striped">
        <thead class="table-dark">
            <tr><th>Produto</th><th>Quantidade</th></tr>
        </thead>
        <tbody>{tabela}</tbody>
    </table>
    </div>

    </div>
    </body>
    </html>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
