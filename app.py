from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2, os

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= CONEXÃO =================
def conectar():
    return psycopg2.connect(
        host="ep-calm-moon-acucwei3-pooler.sa-east-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_zGebRqQWoB06",
        port="5432",
        sslmode="require"
    )

# ================= BANCO =================
def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
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

    conn.commit()
    conn.close()

criar_banco()

# ================= ADMIN =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", ("admin",))
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

# ================= LAYOUT (MENU ESTILO SGP) =================
def layout():
    return """
    <div style="
        background:#1b263b;
        padding:12px;
        display:flex;
        gap:20px;
    ">
        <a href="/dashboard" style="color:white;">Dashboard</a>
        <a href="/saldo" style="color:white;">Saldo</a>
        <a href="/usuarios" style="color:white;">Usuários</a>
        <a href="/logout" style="color:white;">Sair</a>
    </div>
    """

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s", (user,))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], senha):
            session["usuario"] = user
            session["cargo"] = dado[1]

            cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (user,))
            conn.commit()
            conn.close()

            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    <html>
    <body style="margin:0;background:#0d1b2a;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial;">
        <div style="background:#1b263b;padding:30px;border-radius:10px;text-align:center;color:white;width:300px;">
            
            <img src="/static/logo.png" width="120"><br><br>

            <form method="POST">
                <input name="user" placeholder="Usuário" style="width:90%;padding:8px;"><br><br>
                <input name="senha" type="password" placeholder="Senha" style="width:90%;padding:8px;"><br><br>
                <button style="padding:10px;width:100%;">Entrar</button>
                <p style="color:red;">{erro}</p>
            </form>

            <p style="font-size:12px;margin-top:10px;">
                venha conhecer nosso serviço
            </p>

        </div>
    </body>
    </html>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect("/")

    return f"""
    {layout()}
    <div style="padding:20px;color:white;">
        <h2>Bem-vindo {session['usuario']}</h2>
    </div>
    """

# ================= SALDO =================
@app.route("/saldo")
def saldo():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT saldo FROM usuarios WHERE usuario=%s", (session["usuario"],))
    saldo = cursor.fetchone()[0]

    conn.close()

    return f"""
    {layout()}
    <div style="padding:20px;color:white;">
        <h2>Seu saldo: {saldo}</h2>
    </div>
    """

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if "usuario" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return "Não autorizado"

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

    cursor.execute("SELECT usuario, cargo, online FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u, c, o in dados:
        status = "🟢" if o == 1 else "🔴"
        tabela += f"<tr><td>{u}</td><td>{c}</td><td>{status}</td></tr>"

    return f"""
    {layout()}
    <div style="padding:20px;color:white;">
        <h2>Usuários</h2>
        <table border="1" style="color:white;">
            <tr><th>Usuário</th><th>Cargo</th><th>Status</th></tr>
            {tabela}
        </table>
    </div>
    """

# ================= LANÇAR =================
@app.route("/lancar/<usuario>", methods=["POST"])
def lancar(usuario):
    if session.get("cargo") != "admin":
        return "Não autorizado"

    valor = int(request.form["valor"])
    desc = request.form["desc"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE usuario=%s", (valor, usuario))

    cursor.execute("""
        INSERT INTO saldo_historico (usuario, valor, descricao, quem_lancou)
        VALUES (%s,%s,%s,%s)
    """, (usuario, valor, desc, session["usuario"]))

    conn.commit()
    conn.close()

    return redirect("/saldo")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    if "usuario" in session:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("UPDATE usuarios SET online=0 WHERE usuario=%s", (session["usuario"],))

        conn.commit()
        conn.close()

    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
