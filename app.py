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
        cursor.execute("INSERT INTO usuarios VALUES (?,?,?)",
                       ("kaua.barbosa1728@gmail.com",
                        generate_password_hash("997401054"),
                        "admin"))
        conn.commit()

    conn.close()

criar_admin()

# ================= LOGIN (ATUALIZADO) =================
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

body {{
    background: linear-gradient(135deg, #0b1120, #1e293b);
    height:100vh;
    margin:0;
    display:flex;
    align-items:center;
    justify-content:center;
    font-family: 'Segoe UI', sans-serif;
}}

.login-box {{
    width: 400px;
    padding: 40px;
    background:#020617;
    border:1px solid #1e293b;
    border-radius:15px;
    box-shadow: 0 0 30px rgba(0,0,0,0.5);
}}

.title {{
    font-size: 42px;
    font-weight: bold;
    color:#38bdf8;
    text-align:center;
    margin-bottom: 25px;
}}

.subtitle {{
    text-align:center;
    color:#94a3b8;
    margin-bottom: 30px;
}}

input {{
    background:#0b1120 !important;
    border:1px solid #334155 !important;
    color:white !important;
    padding:12px !important;
}}

button {{
    background:#38bdf8 !important;
    border:none !important;
    padding:12px !important;
    font-weight:bold;
}}

button:hover {{
    background:#0ea5e9 !important;
}}

</style>
</head>

<body>

<div class="login-box">
    <div class="title">KBSistemas</div>
    <div class="subtitle">Acesse com seu usuário</div>

    <form method="POST">
        <input name="user" class="form-control mb-3" placeholder="Usuário">
        <input name="senha" type="password" class="form-control mb-3" placeholder="Senha">
        <button class="btn w-100">Entrar</button>
        <p class="text-danger mt-3 text-center">{erro}</p>
    </form>
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

    body {{
        background:#0b1120;
        color:#e5e7eb;
        font-family: 'Segoe UI', sans-serif;
    }}

    .sidebar {{
        width:240px;
        height:100vh;
        background:#020617;
        position:fixed;
        padding:20px;
        border-right:1px solid #1e293b;
    }}

    .sidebar a {{
        display:block;
        color:#94a3b8;
        padding:12px;
        margin-bottom:5px;
        border-radius:8px;
        text-decoration:none;
    }}

    .sidebar a:hover {{
        background:#1e293b;
        color:#38bdf8;
    }}

    .content {{
        margin-left:260px;
        padding:30px;
    }}

    </style>
    </head>

    <body>

    <div class="sidebar">
        <h4>KBSistemas</h4>
        <a href="/dashboard">Dashboard</a>
        <a href="/estoque">Estoque</a>
        <a href="/historico">Histórico</a>
        {"<a href='/admin'>Admin</a>" if session.get("cargo") == "admin" else ""}
        <hr>
        <a href="/logout">Sair</a>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return f"""
    {layout_topo()}
    <div class="content">
    <h2>Dashboard</h2>
    <p>Bem-vindo, {session["user"]}</p>
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

        cursor.execute("INSERT INTO estoque VALUES (?,?,?)", (produto, qtd, categoria))
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
    <h2>Estoque</h2>

    <form method="POST">
    <input name="produto" placeholder="Produto">
    <input name="qtd" type="number" placeholder="Quantidade">
    <input name="categoria" placeholder="Categoria">
    <button>Adicionar</button>
    </form>

    <table class="table text-white">
    <tr><th>Produto</th><th>Qtd</th><th>Categoria</th></tr>
    {tabela}
    </table>

    </div>
    """

# ================= HISTÓRICO =================
@app.route("/historico")
def historico():
    if "user" not in session:
        return redirect("/")

    return f"""
    {layout_topo()}
    <div class="content">
    <h2>Histórico</h2>
    </div>
    """

# ================= ADMIN =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "user" not in session or session["cargo"] != "admin":
        return redirect("/")

    return f"""
    {layout_topo()}
    <div class="content">
    <h2>Admin</h2>
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
