from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= BANCO =================
def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        user TEXT,
        senha TEXT,
        cargo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        produto TEXT,
        quantidade INTEGER,
        tipo TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

criar_banco()

# ================= ADMIN PADRÃO =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE user=?", ("kaua.barbosa1728@gmail.com",))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO usuarios VALUES (?,?,?)
        """, ("kaua.barbosa1728@gmail.com",
              generate_password_hash("997401054"),
              "admin"))
        conn.commit()

    conn.close()

criar_admin()

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT senha, cargo FROM usuarios WHERE user=?", (user,))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]
            conn.close()
            return redirect("/dashboard")

        erro = "Login inválido"
        conn.close()

    return f"""
<!DOCTYPE html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
<style>
body {{background:#2f3e4e;height:100vh;}}
.left {{display:flex;align-items:center;justify-content:center;color:white;}}
.right {{display:flex;align-items:center;justify-content:center;}}
input {{background:#3b4f63 !important;border:none;color:white !important;}}
button {{background:#4a90e2 !important;}}
</style>
</head>
<body>
<div class="container-fluid h-100">
<div class="row h-100">
<div class="col-md-6 left">
<h1 style="font-size:70px;">KBSistemas</h1>
</div>
<div class="col-md-6 right">
<form method="POST" style="width:300px;">
<input name="user" class="form-control mb-3" placeholder="Usuário">
<input name="senha" type="password" class="form-control mb-3" placeholder="Senha">
<button class="btn btn-primary w-100">Acessar</button>
<p class="text-danger mt-2">{erro}</p>
</form>
</div>
</div>
</div>
</body>
</html>
"""

# ================= LAYOUT =================
def layout_topo():
    return f"""
    <html>
    <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
    body {{background:#0f172a;color:white;}}
    .sidebar {{width:220px;height:100vh;background:#020617;position:fixed;padding:20px;}}
    .sidebar a {{display:block;color:#cbd5f5;padding:10px;text-decoration:none;}}
    .sidebar a:hover {{background:#1e293b;}}
    .content {{margin-left:240px;padding:20px;}}
    .card {{background:#020617;border:1px solid #1e293b;border-radius:10px;}}
    input, select {{background:#020617 !important;border:1px solid #334155 !important;color:white !important;}}
    </style>
    </head>
    <body>

    <div class="sidebar">
        <h4>KBSistemas</h4>
        <hr>
        <a href="/dashboard">🏠 Dashboard</a>
        <a href="/estoque">📦 Estoque</a>
        <a href="/historico">📊 Histórico</a>
        {"<a href='/admin'>⚙ Admin</a>" if session["cargo"] == "admin" else ""}
        <hr>
        <p>{session["user"]}</p>
        <a href="/logout" style="color:red;">Sair</a>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM estoque")
    total_prod = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantidade) FROM estoque")
    total_qtd = cursor.fetchone()[0] or 0

    conn.close()

    return f"""
    {layout_topo()}
    <div class="content">
    <h3>Dashboard</h3>

    <div class="row">
        <div class="col-md-4">
            <div class="card p-3">
                <h6>Produtos</h6>
                <h2>{total_prod}</h2>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card p-3">
                <h6>Total Estoque</h6>
                <h2>{total_qtd}</h2>
            </div>
        </div>
    </div>
    </div>
    """

# ================= ESTOQUE =================
@app.route("/estoque", methods=["GET","POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])
        categoria = request.form["categoria"]

        cursor.execute("INSERT INTO estoque VALUES (?,?,?)",
                       (produto, qtd, categoria))

        cursor.execute("""
        INSERT INTO movimentacoes (produto, quantidade, tipo, usuario)
        VALUES (?, ?, ?, ?)
        """, (produto, qtd, "entrada", session["user"]))

        conn.commit()

    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for p, q, c in dados:
        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{c}</td></tr>"

    return f"""
    {layout_topo()}
    <div class="content">

    <h3>Estoque</h3>

    <div class="card p-3 mb-3">
        <form method="POST" class="row">
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
                </select>
            </div>
            <div class="col-md-2">
                <button class="btn btn-success w-100">Adicionar</button>
            </div>
        </form>
    </div>

    <div class="card p-3">
        <table class="table">
        <tr><th>Produto</th><th>Qtd</th><th>Categoria</th></tr>
        {tabela}
        </table>
    </div>

    </div>
    """

# ================= HISTÓRICO =================
@app.route("/historico")
def historico():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movimentacoes ORDER BY data DESC")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>"

    return f"""
    {layout_topo()}
    <div class="content">
    <h3>Histórico</h3>

    <div class="card p-3">
    <table class="table">
    <tr><th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th><th>Data</th></tr>
    {tabela}
    </table>
    </div>

    </div>
    """

# ================= ADMIN =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "user" not in session or session["cargo"] != "admin":
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]
        cargo = request.form["cargo"]

        cursor.execute("INSERT INTO usuarios VALUES (?,?,?)",
                       (user, generate_password_hash(senha), cargo))
        conn.commit()

    cursor.execute("SELECT user, cargo FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u, c in dados:
        tabela += f"<tr><td>{u}</td><td>{c}</td></tr>"

    return f"""
    {layout_topo()}
    <div class="content">

    <h3>Admin</h3>

    <div class="card p-3 mb-3">
    <form method="POST">
        <input name="user" placeholder="Usuário" class="form-control mb-2">
        <input name="senha" placeholder="Senha" class="form-control mb-2">
        <select name="cargo" class="form-control mb-2">
            <option>admin</option>
            <option>operador</option>
        </select>
        <button class="btn btn-warning">Criar usuário</button>
    </form>
    </div>

    <div class="card p-3">
    <table class="table">
    <tr><th>Usuário</th><th>Cargo</th></tr>
    {tabela}
    </table>
    </div>

    </div>
    """

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
