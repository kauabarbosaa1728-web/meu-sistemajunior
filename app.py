from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "segredo123"

def conectar():
    return sqlite3.connect("banco.db")

# BANCO
def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT UNIQUE,
        senha TEXT,
        cargo TEXT,
        online INTEGER DEFAULT 0,
        ultimo_login TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

# CRIAR ADMIN
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE user=?", ("kaua.barbosa1728@gmail.com",))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO usuarios (user, senha, cargo)
        VALUES (?, ?, ?)
        """, ("kaua.barbosa1728@gmail.com", generate_password_hash("997401054"), "admin"))
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
        cursor = conn.cursor()

        cursor.execute("SELECT senha, cargo FROM usuarios WHERE user=?", (user,))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]

            cursor.execute("UPDATE usuarios SET online=1, ultimo_login=CURRENT_TIMESTAMP WHERE user=?", (user,))
            conn.commit()
            conn.close()

            return redirect("/sistema")

        erro = "Login inválido"
        conn.close()

    return f"""
    <html><body style="display:flex;justify-content:center;align-items:center;height:100vh;background:#111;color:white;">
    <form method="POST">
    <h2>KBSistemas</h2>
    <input name="user" placeholder="Usuário"><br><br>
    <input name="senha" type="password" placeholder="Senha"><br><br>
    <button>Entrar</button>
    <p>{erro}</p>
    </form>
    </body></html>
    """

# SISTEMA
@app.route("/sistema")
def sistema():
    if "user" not in session:
        return redirect("/")

    botao_admin = ""
    if session["cargo"] == "admin":
        botao_admin = '<a href="/admin">Painel Admin</a>'

    return f"""
    <h2>Sistema</h2>
    <p>Usuário: {session['user']} ({session['cargo']})</p>
    {botao_admin}
    <br><br>
    <a href="/logout">Sair</a>
    """

# ADMIN
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "user" not in session or session["cargo"] != "admin":
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # CRIAR USUÁRIO
    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]
        cargo = request.form["cargo"]

        cursor.execute("""
        INSERT INTO usuarios (user, senha, cargo)
        VALUES (?, ?, ?)
        """, (user, generate_password_hash(senha), cargo))
        conn.commit()

    cursor.execute("SELECT user, cargo, online FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u, c, o in dados:
        status = "🟢" if o else "🔴"

        tabela += f"""
        <tr>
            <td>{u}</td>
            <td>{c}</td>
            <td>{status}</td>
            <td>
                <form action="/alterar/{u}" method="POST">
                    <input name="senha" placeholder="Nova senha">
                    <button>Alterar</button>
                </form>
            </td>
        </tr>
        """

    return f"""
    <h2>Painel Admin</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário">
        <input name="senha" placeholder="Senha">
        <select name="cargo">
            <option value="admin">Admin</option>
            <option value="operador">Operador</option>
        </select>
        <button>Criar</button>
    </form>

    <table border="1">
    <tr><th>Usuário</th><th>Cargo</th><th>Status</th><th>Ação</th></tr>
    {tabela}
    </table>

    <a href="/sistema">Voltar</a>
    """

# ALTERAR SENHA
@app.route("/alterar/<user>", methods=["POST"])
def alterar(user):
    if session.get("cargo") != "admin":
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    senha = request.form["senha"]

    cursor.execute("UPDATE usuarios SET senha=? WHERE user=?",
                   (generate_password_hash(senha), user))

    conn.commit()
    conn.close()

    return redirect("/admin")

# LOGOUT
@app.route("/logout")
def logout():
    conn = conectar()
    cursor = conn.cursor()

    if "user" in session:
        cursor.execute("UPDATE usuarios SET online=0 WHERE user=?", (session["user"],))
        conn.commit()

    conn.close()
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
