from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "segredo123"

def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS usuarios (user TEXT, senha TEXT, cargo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS estoque (produto TEXT, quantidade INT, categoria TEXT)")
    c.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
        produto TEXT, quantidade INT, tipo TEXT, usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

criar_banco()

def criar_admin():
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM usuarios WHERE user=?", ("kaua.barbosa1728@gmail.com",))
    if not c.fetchone():
        c.execute("INSERT INTO usuarios VALUES (?,?,?)",
                  ("kaua.barbosa1728@gmail.com",
                   generate_password_hash("997401054"),
                   "admin"))
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
        c = conn.cursor()
        c.execute("SELECT senha, cargo FROM usuarios WHERE user=?", (user,))
        dado = c.fetchone()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    <html>
    <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body style="background:#0b1120;display:flex;justify-content:center;align-items:center;height:100vh;">

    <form method="POST" style="width:300px;">
    <h3>Login</h3>
    <input name="user" class="form-control mb-2" placeholder="Usuário">
    <input name="senha" type="password" class="form-control mb-2" placeholder="Senha">
    <button class="btn btn-primary w-100">Entrar</button>
    <p style="color:red;">{erro}</p>
    </form>

    </body>
    </html>
    """

# LAYOUT
def layout():
    return f"""
    <html>
    <head>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">

    <!-- ANIMAÇÃO -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css" rel="stylesheet">

    <style>
    body {{background:#0b1120;color:white;}}
    .sidebar {{width:220px;height:100vh;background:#020617;position:fixed;padding:20px;}}
    .sidebar a {{display:block;color:#94a3b8;padding:10px;text-decoration:none;}}
    .sidebar a:hover {{background:#1e293b;color:#38bdf8;}}
    .content {{margin-left:240px;padding:30px;}}
    .card {{background:#020617;padding:20px;border-radius:10px;}}
    </style>

    </head>

    <body>

    <div class="sidebar">
    <h4>KBSistemas</h4>
    <a href="/dashboard">Dashboard</a>
    <a href="/estoque">Estoque</a>
    <a href="/historico">Histórico</a>
    {"<a href='/admin'>Admin</a>" if session["cargo"]=="admin" else ""}
    <hr>
    <a href="/logout">Sair</a>
    </div>
    """

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT categoria, SUM(quantidade) FROM estoque GROUP BY categoria")
    dados = c.fetchall()

    categorias = [d[0] for d in dados]
    quantidades = [d[1] for d in dados]

    return f"""
    {layout()}
    <div class="content">

    <h3 data-aos="fade-up">Dashboard</h3>

    <canvas id="grafico" data-aos="zoom-in"></canvas>

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

    <script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"></script>
    <script>AOS.init();</script>

    </body></html>
    """

# ESTOQUE
@app.route("/estoque", methods=["GET","POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    busca = request.args.get("busca", "")

    if request.method == "POST":
        p = request.form["produto"]
        q = int(request.form["qtd"])
        cat = request.form["categoria"]

        c.execute("INSERT INTO estoque VALUES (?,?,?)", (p,q,cat))
        c.execute("INSERT INTO movimentacoes VALUES (?,?,?,?,datetime('now'))",
                  (p,q,"entrada",session["user"]))
        conn.commit()

    if busca:
        c.execute("SELECT * FROM estoque WHERE produto LIKE ?", (f"%{busca}%",))
    else:
        c.execute("SELECT * FROM estoque")

    dados = c.fetchall()

    tabela = ""
    for p,q,cg in dados:
        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{cg}</td><td><a href='/saida/{p}' class='btn btn-warning btn-sm'>Saída</a></td></tr>"

    return f"""
    {layout()}
    <div class="content">

    <h3 data-aos="fade-up">Estoque</h3>

    <form method="GET">
    <input name="busca" class="form-control mb-3" placeholder="Buscar produto">
    </form>

    <div class="card mb-3">
    <form method="POST" class="row">
    <div class="col-md-4"><input name="produto" class="form-control"></div>
    <div class="col-md-3"><input name="qtd" type="number" class="form-control"></div>
    <div class="col-md-3"><select name="categoria" class="form-control">
    <option>Eletrônicos</option><option>Ferramentas</option></select></div>
    <div class="col-md-2"><button class="btn btn-success w-100">Add</button></div>
    </form>
    </div>

    <div class="card">
    <table class="table text-white">
    <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ação</th></tr>
    {tabela}
    </table>
    </div>

    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"></script>
    <script>AOS.init();</script>

    </body></html>
    """

# SAÍDA
@app.route("/saida/<produto>")
def saida(produto):
    conn = conectar()
    c = conn.cursor()

    c.execute("UPDATE estoque SET quantidade = quantidade-1 WHERE produto=?", (produto,))
    c.execute("INSERT INTO movimentacoes VALUES (?,?,?,?,datetime('now'))",
              (produto,1,"saida",session["user"]))
    conn.commit()

    return redirect("/estoque")

# HISTÓRICO
@app.route("/historico")
def historico():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM movimentacoes ORDER BY data DESC")
    dados = c.fetchall()

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>"

    return f"""
    {layout()}
    <div class="content">

    <h3 data-aos="fade-up">Histórico</h3>

    <div class="card">
    <table class="table text-white">
    <tr><th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th><th>Data</th></tr>
    {tabela}
    </table>
    </div>

    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"></script>
    <script>AOS.init();</script>

    </body></html>
    """

# ADMIN
@app.route("/admin", methods=["GET","POST"])
def admin():
    if session.get("cargo") != "admin":
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        u = request.form["user"]
        s = request.form["senha"]
        cargo = request.form["cargo"]

        c.execute("INSERT INTO usuarios VALUES (?,?,?)",
                  (u, generate_password_hash(s), cargo))
        conn.commit()

    c.execute("SELECT user, cargo FROM usuarios")
    dados = c.fetchall()

    tabela = ""
    for u,cg in dados:
        tabela += f"<tr><td>{u}</td><td>{cg}</td></tr>"

    return f"""
    {layout()}
    <div class="content">

    <h3 data-aos="fade-up">Admin</h3>

    <div class="card mb-3">
    <form method="POST">
    <input name="user" class="form-control mb-2" placeholder="Usuário">
    <input name="senha" class="form-control mb-2" placeholder="Senha">
    <select name="cargo" class="form-control mb-2">
    <option>admin</option><option>operador</option></select>
    <button class="btn btn-warning">Criar</button>
    </form>
    </div>

    <div class="card">
    <table class="table text-white">
    <tr><th>Usuário</th><th>Cargo</th></tr>
    {tabela}
    </table>
    </div>

    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"></script>
    <script>AOS.init();</script>

    </body></html>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
