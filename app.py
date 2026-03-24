from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= ESTILO =================
def estilo():
    return """
    <style>
    body { margin: 0; font-family: Arial; background: #0f172a; color: white; }
    .container { padding: 20px; }
    .card { background: #020617; padding: 20px; border-radius: 10px; margin-top: 15px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; border-bottom: 1px solid #1e293b; }
    th { background: #1e293b; }
    input { padding: 8px; margin: 5px; border-radius: 5px; border: none; width: 100%; }
    button { padding: 10px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; }
    a { color: #3b82f6; }
    </style>
    """

# ================= BANCO =================
def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        user TEXT, senha TEXT, cargo TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque (
        produto TEXT, quantidade INTEGER, categoria TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
        produto TEXT,
        quantidade INTEGER,
        tipo TEXT,
        usuario TEXT,
        local_saida TEXT,
        destino TEXT,
        observacao TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

criar_banco()

# ================= ADMIN =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    if not cursor.execute("SELECT * FROM usuarios WHERE user=?", ("admin",)).fetchone():
        cursor.execute("INSERT INTO usuarios VALUES (?,?,?)",
                       ("admin", generate_password_hash("123"), "admin"))

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
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    {estilo()}
    <body style="display:flex;justify-content:center;align-items:center;height:100vh;">
    <div class="card" style="width:320px;text-align:center;">
        <h1>KBSISTEMAS</h1>
        <form method="POST">
            <input name="user" placeholder="Usuário"><br>
            <input name="senha" type="password" placeholder="Senha"><br>
            <button>Entrar</button>
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
        <a href="/logout">Sair</a>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return f"{estilo()}{layout()}<div class='container'><div class='card'><h2>Bem-vindo {session['user']}</h2></div></div>"

# ================= ESTOQUE =================
@app.route("/estoque", methods=["GET","POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("INSERT INTO estoque VALUES (?,?,?)",
                       (request.form["produto"], int(request.form["qtd"]), request.form["categoria"]))
        conn.commit()

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
            <td><a href="/saida/{p}">Saída</a></td>
        </tr>
        """

    return f"""
    {estilo()}{layout()}
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
                <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ação</th></tr>
                {tabela}
            </table>
        </div>
    </div>
    """

# ================= SAÍDA COM DETALHES =================
@app.route("/saida/<produto>", methods=["GET","POST"])
def saida(produto):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        local = request.form["local"]
        destino = request.form["destino"]
        obs = request.form["obs"]

        cursor.execute("SELECT quantidade FROM estoque WHERE produto=?", (produto,))
        q = cursor.fetchone()

        if not q or q[0] <= 0:
            return "⚠️ Estoque zerado"

        cursor.execute("UPDATE estoque SET quantidade = quantidade - 1 WHERE produto=?", (produto,))

        cursor.execute("""
        INSERT INTO movimentacoes (produto, quantidade, tipo, usuario, local_saida, destino, observacao)
        VALUES (?,?,?,?,?,?,?)
        """, (produto, 1, "saida", session["user"], local, destino, obs))

        conn.commit()
        conn.close()

        return redirect("/estoque")

    return f"""
    {estilo()}{layout()}
    <div class="container">
        <div class="card">
            <h2>Saída: {produto}</h2>
            <form method="POST">
                <input name="local" placeholder="Local de saída">
                <input name="destino" placeholder="Destino">
                <input name="obs" placeholder="Observação">
                <button>Confirmar</button>
            </form>
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
        tabela += f"""
        <tr>
            <td>{d[0]}</td>
            <td>{d[1]}</td>
            <td>{d[2]}</td>
            <td>{d[3]}</td>
            <td>{d[4]}</td>
            <td>{d[5]}</td>
            <td>{d[6]}</td>
            <td>{d[7]}</td>
        </tr>
        """

    return f"""
    {estilo()}{layout()}
    <div class="container">
        <div class="card">
            <h2>Histórico</h2>
            <table>
                <tr>
                    <th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th>
                    <th>Local</th><th>Destino</th><th>Obs</th><th>Data</th>
                </tr>
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
    app.run(debug=True)
