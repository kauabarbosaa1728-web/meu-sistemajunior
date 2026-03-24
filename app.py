from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2, os

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= ESTILO =================
def estilo():
    return """
    <style>
    body {
        margin: 0;
        font-family: Arial;
        background: #0f172a;
        color: white;
    }

    .container { padding: 20px; }

    .card {
        background: #020617;
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th, td {
        padding: 10px;
        border-bottom: 1px solid #1e293b;
    }

    th { background: #1e293b; }

    input, select {
        padding: 8px;
        margin: 5px;
        border-radius: 5px;
        border: none;
    }

    button {
        padding: 10px;
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    a { color: #3b82f6; }
    </style>
    """

# ================= BANCO (NEON) =================
def conectar():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_zGebRqQWoB06@ep-calm-moon-acucwei3-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        user TEXT,
        senha TEXT,
        cargo TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque (
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
        produto TEXT,
        quantidade INTEGER,
        tipo TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

criar_banco()

# ================= ADMIN =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    usuarios_fixos = [
        ("admin", "123", "admin"),
        ("kaua.barbosa1728@gmail.com", "997401054", "admin")
    ]

    for user, senha, cargo in usuarios_fixos:
        cursor.execute("SELECT * FROM usuarios WHERE user=%s", (user,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios VALUES (%s,%s,%s)",
                           (user, generate_password_hash(senha), cargo))

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

        cursor.execute("SELECT senha, cargo FROM usuarios WHERE user=%s", (user,))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    {estilo()}

    <body style="display:flex;justify-content:center;align-items:center;height:100vh;">
    <div class="card" style="width:320px;text-align:center;">
        <h1 style="font-size:40px;">KBSISTEMAS</h1>

        <form method="POST">
            <input name="user" placeholder="Usuário" style="width:100%"><br>
            <input name="senha" type="password" placeholder="Senha" style="width:100%"><br>

            <button style="width:100%">Entrar</button>
            <p style="color:red;">{erro}</p>
        </form>
    </div>
    </body>
    """

# ================= MENU =================
def layout():
    return f"""
    <div class="card">
        <a href="/dashboard">Dashboard</a> |
        <a href="/estoque">Estoque</a> |
        <a href="/historico">Histórico</a> |
        <a href="/usuarios">Usuários</a> |
        <a href="/logout">Sair</a>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return f"""
    {estilo()}
    {layout()}

    <div class="container">
        <div class="card">
            <h2>Bem-vindo {session["user"]}</h2>
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
        cursor.execute("INSERT INTO estoque VALUES (%s,%s,%s)",
                       (request.form["produto"], int(request.form["qtd"]), request.form["categoria"]))

        cursor.execute("INSERT INTO movimentacoes (produto, quantidade, tipo, usuario) VALUES (%s,%s,%s,%s)",
                       (request.form["produto"], int(request.form["qtd"]), "entrada", session["user"]))

        conn.commit()

    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for p, q, c in dados:
        cor = "#ef4444" if q <= 5 else "white"
        alerta = "⚠️" if q <= 5 else ""

        tabela += f"""
        <tr style="color:{cor}">
            <td>{p} {alerta}</td>
            <td>{q}</td>
            <td>{c}</td>
            <td>
                <a href="/saida/{p}">Saída</a> |
                <a href="/historico_produto/{p}">Histórico</a>
            </td>
        </tr>
        """

    return f"""
    {estilo()}
    {layout()}

    <div class="container">
    <div class="card">
        <h2>📦 Estoque</h2>

        <form method="POST">
            <input name="produto" placeholder="Produto">
            <input name="qtd" type="number" placeholder="Qtd">
            <input name="categoria" placeholder="Categoria">
            <button>Adicionar</button>
        </form>
    </div>

    <div class="card">
        <table>
            <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ações</th></tr>
            {tabela}
        </table>
    </div>
    </div>
    """

# ================= SAÍDA =================
@app.route("/saida/<produto>")
def saida(produto):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT quantidade FROM estoque WHERE produto=%s", (produto,))
    dado = cursor.fetchone()

    if not dado or dado[0] <= 0:
        return "⚠️ Estoque zerado"

    cursor.execute("UPDATE estoque SET quantidade = quantidade - 1 WHERE produto=%s", (produto,))

    cursor.execute("INSERT INTO movimentacoes (produto, quantidade, tipo, usuario) VALUES (%s,%s,%s,%s)",
                   (produto, 1, "saida", session["user"]))

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
    {estilo()}
    {layout()}

    <div class="container">
        <div class="card">
            <h2>Histórico</h2>
            <table>
                <tr><th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th><th>Data</th></tr>
                {tabela}
            </table>
        </div>
    </div>
    """

# ================= HISTÓRICO PRODUTO =================
@app.route("/historico_produto/<produto>")
def historico_produto(produto):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movimentacoes WHERE produto=%s ORDER BY data DESC", (produto,))
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>"

    return f"""
    {estilo()}
    {layout()}

    <div class="container">
        <div class="card">
            <h2>Histórico do Produto: {produto}</h2>
            <table>
                <tr><th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th><th>Data</th></tr>
                {tabela}
            </table>
        </div>
    </div>
    """

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if "user" not in session or session["cargo"] != "admin":
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("INSERT INTO usuarios VALUES (%s,%s,%s)",
            (request.form["user"], generate_password_hash(request.form["senha"]), request.form["cargo"]))
        conn.commit()

    cursor.execute("SELECT user, cargo FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u, c in dados:
        tabela += f"<tr><td>{u}</td><td>{c}</td></tr>"

    return f"""
    {estilo()}
    {layout()}

    <div class="container">

    <div class="card">
        <h2>Criar Usuário</h2>

        <form method="POST">
            <input name="user" placeholder="Usuário">
            <input name="senha" type="password" placeholder="Senha">

            <select name="cargo">
                <option value="admin">Admin</option>
                <option value="operador">Operador</option>
                <option value="visualizacao">Visualização</option>
            </select>

            <button>Criar</button>
        </form>
    </div>

    <div class="card">
        <table>
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
