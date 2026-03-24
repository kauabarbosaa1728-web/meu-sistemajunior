from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
        senha TEXT,
        cargo TEXT,
        saldo INTEGER DEFAULT 0,
        pode_estoque INTEGER DEFAULT 1,
        pode_usuarios INTEGER DEFAULT 1,
        online INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )
    """)

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
        INSERT INTO usuarios (usuario, senha, cargo, saldo, pode_estoque, pode_usuarios, online)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, ("admin", generate_password_hash("123"), "admin", 0,1,1,0))

    conn.commit()
    conn.close()

criar_admin()

# ================= TOPO (SGP STYLE) =================
def topo():
    return f"""
    <div style="
        position:fixed;
        top:0;
        left:0;
        width:100%;
        height:60px;
        background:#0a192f;
        color:white;
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding:0 20px;
        box-shadow:0 2px 10px rgba(0,0,0,0.5);
    ">

        <div style="font-weight:bold;font-size:20px;color:#3a86ff;">
            ⚡ KB Sistemas
        </div>

        <div>
            <a href="/dashboard" style="color:white;margin:0 10px;text-decoration:none;">Dashboard</a>
            <a href="/estoque" style="color:white;margin:0 10px;text-decoration:none;">Estoque</a>
            <a href="/usuarios" style="color:white;margin:0 10px;text-decoration:none;">Usuários</a>
            <a href="/saldo" style="color:white;margin:0 10px;text-decoration:none;">Saldo</a>
            <a href="/logout" style="color:red;margin:0 10px;text-decoration:none;">Sair</a>
        </div>

    </div>
    """

def container(conteudo):
    return f"""
    {topo()}
    <div style="
        margin-top:70px;
        padding:20px;
        background:linear-gradient(135deg,#0a192f,#1b263b);
        min-height:100vh;
        color:white;
    ">
        {conteudo}
    </div>
    """

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        usuario = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s", (usuario,))
        dado = cursor.fetchone()

        conn.close()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = usuario
            session["cargo"] = dado[1]
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    <html>
    <body style="
        margin:0;
        background:#0a192f;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        color:white;
    ">

    <div style="background:#1b263b;padding:40px;border-radius:10px;text-align:center;">

        <h2 style="color:#3a86ff;">⚡ KB Sistemas</h2>

        <p>Bem-vindo 👋</p>

        <form method="POST">
            <input name="user" placeholder="Usuário"><br><br>
            <input name="senha" type="password" placeholder="Senha"><br><br>
            <button>Entrar</button>
        </form>

        <p style="color:red;">{erro}</p>

    </div>

    </body>
    </html>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return container(f"<h1>Dashboard</h1><p>Bem-vindo {session['user']}</p>")

# ================= ESTOQUE =================
@app.route("/estoque", methods=["GET","POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO estoque (produto, quantidade, categoria)
        VALUES (%s,%s,%s)
        """, (
            request.form["produto"],
            request.form["quantidade"],
            request.form["categoria"]
        ))
        conn.commit()

    cursor.execute("SELECT produto, quantidade, categoria FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for p,q,c in dados:
        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{c}</td></tr>"

    return container(f"""
    <h2>Estoque</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="quantidade" placeholder="Quantidade">
        <input name="categoria" placeholder="Categoria">
        <button>Adicionar</button>
    </form>

    <table border="1" style="color:white;">
        <tr><th>Produto</th><th>Qtd</th><th>Categoria</th></tr>
        {tabela}
    </table>
    """)

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if session.get("cargo") != "admin":
        return "Não autorizado"

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO usuarios (usuario, senha, cargo, saldo, pode_estoque, pode_usuarios, online)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form["user"],
            generate_password_hash(request.form["senha"]),
            request.form["cargo"],
            0,1,1,0
        ))
        conn.commit()

    cursor.execute("SELECT usuario, cargo, online FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u,c,o in dados:
        status = "🟢" if o else "🔴"
        tabela += f"<tr><td>{u}</td><td>{c}</td><td>{status}</td></tr>"

    return container(f"""
    <h2>Usuários</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário">
        <input name="senha" type="password" placeholder="Senha">
        <select name="cargo">
            <option>admin</option>
            <option>operador</option>
        </select>
        <button>Criar</button>
    </form>

    <table border="1" style="color:white;">
        <tr><th>Usuário</th><th>Cargo</th><th>Status</th></tr>
        {tabela}
    </table>
    """)

# ================= SALDO =================
@app.route("/saldo")
def saldo():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT saldo FROM usuarios WHERE usuario=%s", (session["user"],))
    saldo = cursor.fetchone()[0]

    conn.close()

    return container(f"<h2>Saldo: {saldo}</h2>")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
