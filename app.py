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

    cursor.execute("SELECT * FROM usuarios WHERE user=?", ("admin",))
    if not cursor.fetchone():
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
            conn.close()
            return redirect("/dashboard")

        erro = "Login inválido"
        conn.close()

    return f"""
    <html>
    <body style="display:flex;justify-content:center;align-items:center;height:100vh;">
        <form method="POST">
            <input name="user" placeholder="Usuário"><br><br>
            <input name="senha" type="password" placeholder="Senha"><br><br>
            <button>Entrar</button>
            <p>{erro}</p>
        </form>
    </body>
    </html>
    """

# ================= LAYOUT =================
def layout():
    return f"""
    <div style="background:#222;padding:10px;color:white;">
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

    return f"""
    {layout()}
    <h2>Dashboard</h2>
    <p>Bem-vindo {session["user"]}</p>
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

        cor = "red" if q <= 5 else "black"
        alerta = "⚠️" if q <= 5 else ""

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

# ================= EDITAR =================
@app.route("/editar/<produto>", methods=["GET","POST"])
def editar(produto):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        qtd = int(request.form["qtd"])
        categoria = request.form["categoria"]

        cursor.execute("""
        UPDATE estoque SET quantidade=?, categoria=? WHERE produto=?
        """, (qtd, categoria, produto))

        conn.commit()
        conn.close()
        return redirect("/estoque")

    cursor.execute("SELECT * FROM estoque WHERE produto=?", (produto,))
    dado = cursor.fetchone()
    conn.close()

    return f"""
    {layout()}
    <h2>Editar Produto</h2>

    <form method="POST">
        <input name="qtd" value="{dado[1]}">
        <input name="categoria" value="{dado[2]}">
        <button>Salvar</button>
    </form>
    """

# ================= SAÍDA =================
@app.route("/saida/<produto>")
def saida(produto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT quantidade FROM estoque WHERE produto=?", (produto,))
    dado = cursor.fetchone()

    if not dado or dado[0] <= 0:
        conn.close()
        return "⚠️ Estoque zerado, saída bloqueada!"

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
    {layout()}
    <h2>Histórico</h2>

    <table border="1">
        <tr><th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th><th>Data</th></tr>
        {tabela}
    </table>
    """

# ================= HISTÓRICO POR PRODUTO =================
@app.route("/historico_produto/<produto>")
def historico_produto(produto):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM movimentacoes WHERE produto=? ORDER BY data DESC
    """, (produto,))

    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>"

    return f"""
    {layout()}
    <h2>Histórico do Produto: {produto}</h2>

    <table border="1">
        <tr><th>Produto</th><th>Qtd</th><th>Tipo</th><th>Usuário</th><th>Data</th></tr>
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
