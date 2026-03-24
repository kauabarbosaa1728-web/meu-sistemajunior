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

# ================= BANCO =================
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

# ================= ADMIN GARANTIDO =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    # apaga se já existir e recria
    cursor.execute("DELETE FROM usuarios WHERE user=%s", ("kaua.barbosa1728@gmail.com",))

    cursor.execute("INSERT INTO usuarios VALUES (%s,%s,%s)",
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
    return """
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
        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{c}</td></tr>"

    return f"""
    {estilo()}
    {layout()}
    <div class="container">
        <div class="card">
            <h2>Estoque</h2>

            <form method="POST">
                <input name="produto" placeholder="Produto">
                <input name="qtd" type="number" placeholder="Qtd">
                <input name="categoria" placeholder="Categoria">
                <button>Adicionar</button>
            </form>
        </div>

        <div class="card">
            <table>
                <tr><th>Produto</th><th>Qtd</th><th>Categoria</th></tr>
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
