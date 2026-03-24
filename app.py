from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2, os

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= CONEXÃO NEON =================
def conectar():
    return psycopg2.connect(
        host="ep-calm-moon-acucwei3-pooler.sa-east-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_zGebRqQWoB06",
        port="5432",
        sslmode="require"
    )

# ================= CRIAR TABELAS =================
def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        user TEXT PRIMARY KEY,
        senha TEXT,
        cargo TEXT,
        pode_estoque INTEGER DEFAULT 1,
        pode_historico INTEGER DEFAULT 1,
        pode_usuarios INTEGER DEFAULT 0,
        online INTEGER DEFAULT 0,
        saldo INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS saldo_historico (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        valor INTEGER,
        descricao TEXT,
        quem_lancou TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque (
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
        id SERIAL PRIMARY KEY,
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

    cursor.execute("SELECT * FROM usuarios WHERE user=%s", ("admin",))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO usuarios VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            "admin",
            generate_password_hash("123"),
            "admin",
            1, 1, 1, 0, 0
        ))

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

            cursor.execute("UPDATE usuarios SET online=1 WHERE user=%s", (user,))
            conn.commit()
            conn.close()

            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    <h2>Login</h2>
    <form method="POST">
        <input name="user" placeholder="Usuário"><br>
        <input name="senha" type="password" placeholder="Senha"><br>
        <button>Entrar</button>
        <p style="color:red;">{erro}</p>
    </form>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return f"<h2>Bem-vindo {session['user']}</h2>"

# ================= SALDO =================
@app.route("/saldo")
def saldo():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT saldo FROM usuarios WHERE user=%s", (session["user"],))
    saldo = cursor.fetchone()[0]

    conn.close()

    return f"<h2>Seu saldo: {saldo}</h2>"

# ================= EXTRATO =================
@app.route("/extrato/<usuario>")
def extrato(usuario):
    if "user" not in session:
        return redirect("/")

    if session["user"] != usuario and session["cargo"] != "admin":
        return "Não autorizado. Falar com o administrador."

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT valor, descricao, quem_lancou, data 
        FROM saldo_historico 
        WHERE usuario=%s
        ORDER BY data DESC
    """, (usuario,))

    dados = cursor.fetchall()
    conn.close()

    return str(dados)

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return "Não autorizado. Falar com o administrador."

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            INSERT INTO usuarios VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form["user"],
            generate_password_hash(request.form["senha"]),
            request.form["cargo"],
            1, 1, 1, 0, 0
        ))
        conn.commit()

    cursor.execute("SELECT user, cargo, online FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    return str(dados)

# ================= LANÇAR SALDO =================
@app.route("/lancar/<usuario>", methods=["GET","POST"])
def lancar(usuario):
    if session.get("cargo") != "admin":
        return "Não autorizado. Falar com o administrador."

    if request.method == "POST":
        valor = int(request.form["valor"])
        desc = request.form["desc"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuarios 
            SET saldo = saldo + %s 
            WHERE user=%s
        """, (valor, usuario))

        cursor.execute("""
            INSERT INTO saldo_historico (usuario, valor, descricao, quem_lancou)
            VALUES (%s,%s,%s,%s)
        """, (usuario, valor, desc, session["user"]))

        conn.commit()
        conn.close()

        return redirect("/saldo")

    return """
    <form method="POST">
        <input name="valor" placeholder="Valor">
        <input name="desc" placeholder="Descrição">
        <button>Lançar</button>
    </form>
    """

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    if "user" in session:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("UPDATE usuarios SET online=0 WHERE user=%s", (session["user"],))

        conn.commit()
        conn.close()

    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
