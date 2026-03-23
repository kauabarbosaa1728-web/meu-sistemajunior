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

# ================= ADMIN PADRÃO + SEU LOGIN =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    # admin padrão
    cursor.execute("SELECT * FROM usuarios WHERE user=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios VALUES (?,?,?)",
                       ("admin", generate_password_hash("123"), "admin"))

    # SEU ADMIN
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
    <html>
    <body style="
        margin:0;
        background:#0f172a;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
        font-family:Arial;
    ">
    <div style="background:#020617;padding:40px;border-radius:10px;text-align:center;">

        <h1 style="font-size:40px;">KBSISTEMAS</h1>

        <form method="POST">
            <input name="user" placeholder="Usuário" style="padding:10px;width:100%;margin:5px;"><br>
            <input name="senha" type="password" placeholder="Senha" style="padding:10px;width:100%;margin:5px;"><br>

            <button style="padding:10px;width:100%;background:#3b82f6;color:white;">Entrar</button>
            <p style="color:red;">{erro}</p>
        </form>

    </div>
    </body>
    </html>
    """

# ================= MENU =================
def layout():
    return f"""
    <div style="background:#020617;padding:15px;color:white;">
        <a href="/dashboard" style="color:white;">Dashboard</a> |
        <a href="/estoque" style="color:white;">Estoque</a> |
        <a href="/historico" style="color:white;">Histórico</a> |
        <a href="/usuarios" style="color:white;">Usuários</a> |
        <a href="/logout" style="color:white;">Sair</a>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return f"""
    {layout()}
    <h2>Bem-vindo {session["user"]}</h2>
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
        INSERT INTO movimentacoes VALUES (?,?,?,?,CURRENT_TIMESTAMP)
        """, (produto, qtd, "entrada", session["user"]))

        conn.commit()

    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""

    for p, q, c in dados:

        cor = "#ef4444" if q <= 5 else "#e5e7eb"
        alerta = "⚠️ BAIXO" if q <= 5 else ""

        tabela += f"""
        <tr style="color:{cor}">
            <td>{p} {alerta}</td>
            <td>{q}</td>
            <td>{c}</td>
            <td>
                <a href="/saida/{p}">Saída</a> |
                <a href="/editar/{p}">Editar</a> |
                <a href="/historico_produto/{p}">Histórico</a>
            </td>
        </tr>
        """

    return f"""
    {layout()}

    <h2>Estoque</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" type="number" placeholder="Qtd">
        <input name="categoria" placeholder="Categoria">
        <button>Adicionar</button>
    </form>

    <table border="1">
        <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ações</th></tr>
        {tabela}
    </table>
    """

# ================= SAÍDA =================
@app.route("/saida/<produto>")
def saida(produto):

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT quantidade FROM estoque WHERE produto=?", (produto,))
    dado = cursor.fetchone()

    if not dado or dado[0] <= 0:
        conn.close()
        return "⚠️ Estoque zerado!"

    cursor.execute("UPDATE estoque SET quantidade = quantidade - 1 WHERE produto=?", (produto,))

    cursor.execute("""
    INSERT INTO movimentacoes VALUES (?,?,?,?,CURRENT_TIMESTAMP)
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
    {layout()}
    <table border="1">
        <tr><th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th><th>Data</th></tr>
        {tabela}
    </table>
    """

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
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
    {layout()}
    <h2>Usuários</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário">
        <input name="senha" placeholder="Senha">
        <select name="cargo">
            <option>admin</option>
            <option>operador</option>
            <option>visualizador</option>
        </select>
        <button>Criar</button>
    </form>

    <table border="1">
        <tr><th>Usuário</th><th>Cargo</th></tr>
        {tabela}
    </table>
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
