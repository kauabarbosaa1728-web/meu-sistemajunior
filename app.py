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

# ================= LAYOUT PREMIUM =================
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

    .sidebar h4 {{
        color:#38bdf8;
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

    .topbar {{
        background:#020617;
        padding:15px;
        border-radius:10px;
        margin-bottom:20px;
        display:flex;
        justify-content:space-between;
        border:1px solid #1e293b;
    }}

    .card {{
        background:#020617;
        border:1px solid #1e293b;
        border-radius:12px;
    }}

    input, select {{
        background:#020617 !important;
        border:1px solid #334155 !important;
        color:white !important;
    }}

    </style>
    </head>

    <body>

    <div class="sidebar">
        <h4>KBSistemas</h4>
        <a href="/dashboard">Dashboard</a>
        <a href="/estoque">Estoque</a>
        <a href="/historico">Histórico</a>
        {"<a href='/admin'>Admin</a>" if session["cargo"] == "admin" else ""}
        <hr>
        <a href="/logout">Sair</a>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT categoria, SUM(quantidade) FROM estoque GROUP BY categoria")
    dados = cursor.fetchall()

    categorias = [d[0] for d in dados]
    quantidades = [d[1] for d in dados]

    conn.close()

    return f"""
    {layout_topo()}
    <div class="content">

    <div class="topbar">
    <h4>Dashboard</h4>
    <span>{session["user"]}</span>
    </div>

    <canvas id="grafico"></canvas>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
    new Chart(document.getElementById('grafico'), {{
        type: 'bar',
        data: {{
            labels: {categorias},
            datasets: [{{ data: {quantidades} }}]
        }}
    }});
    </script>

    </div>
    """

# ================= ESTOQUE =================
@app.route("/estoque", methods=["GET","POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    busca = request.args.get("busca", "")

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

    if busca:
        cursor.execute("SELECT * FROM estoque WHERE produto LIKE ?", (f"%{busca}%",))
    else:
        cursor.execute("SELECT * FROM estoque")

    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for p, q, c in dados:
        tabela += f"""
        <tr>
        <td>{p}</td>
        <td>{q}</td>
        <td>{c}</td>
        <td><a href="/saida/{p}" class="btn btn-warning btn-sm">Saída</a></td>
        </tr>
        """

    return f"""
    {layout_topo()}
    <div class="content">

    <div class="topbar"><h4>Estoque</h4></div>

    <form method="GET">
    <input name="busca" class="form-control mb-3" placeholder="Buscar produto">
    </form>

    <div class="card p-3 mb-3">
    <form method="POST" class="row">
    <div class="col-md-4"><input name="produto" class="form-control"></div>
    <div class="col-md-3"><input name="qtd" type="number" class="form-control"></div>
    <div class="col-md-3"><select name="categoria" class="form-control">
    <option>Eletrônicos</option><option>Ferramentas</option></select></div>
    <div class="col-md-2"><button class="btn btn-success w-100">Add</button></div>
    </form>
    </div>

    <div class="card p-3">
    <table class="table">
    <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ação</th></tr>
    {tabela}
    </table>
    </div>

    </div>
    """

# ================= SAÍDA =================
@app.route("/saida/<produto>")
def saida(produto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE estoque SET quantidade = quantidade - 1 WHERE produto=?", (produto,))
    cursor.execute("""
    INSERT INTO movimentacoes (produto, quantidade, tipo, usuario)
    VALUES (?, ?, ?, ?)
    """, (produto, 1, "saida", session["user"]))

    conn.commit()
    conn.close()

    return redirect("/estoque")

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
    <div class="topbar"><h4>Histórico</h4></div>
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
        tabela += f"""
        <tr>
        <td>{u}</td>
        <td>{c}</td>
        <td>
        <form action="/alterar/{u}" method="POST">
        <input name="senha" placeholder="Nova senha">
        <button class="btn btn-warning btn-sm">Alterar</button>
        </form>
        </td>
        </tr>
        """

    return f"""
    {layout_topo()}
    <div class="content">
    <div class="topbar"><h4>Admin</h4></div>

    <div class="card p-3 mb-3">
    <form method="POST">
    <input name="user" class="form-control mb-2" placeholder="Usuário">
    <input name="senha" class="form-control mb-2" placeholder="Senha">
    <select name="cargo" class="form-control mb-2">
    <option>admin</option><option>operador</option></select>
    <button class="btn btn-warning">Criar</button>
    </form>
    </div>

    <div class="card p-3">
    <table class="table">
    <tr><th>Usuário</th><th>Cargo</th><th>Ação</th></tr>
    {tabela}
    </table>
    </div>

    </div>
    """

@app.route("/alterar/<user>", methods=["POST"])
def alterar(user):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE usuarios SET senha=? WHERE user=?",
                   (generate_password_hash(request.form["senha"]), user))

    conn.commit()
    conn.close()
    return redirect("/admin")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
