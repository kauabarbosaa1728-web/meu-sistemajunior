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
        saldo INTEGER DEFAULT 0
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
        INSERT INTO usuarios VALUES (%s,%s,%s,%s)
        """, ("admin", generate_password_hash("123"), "admin", 0))

    conn.commit()
    conn.close()

criar_admin()

# ================= MENU TOP =================
def topo():
    return """
    <style>
    body {margin:0;background:#0f172a;color:white;font-family:Arial;}
    .menu {background:#1e293b;padding:10px;display:flex;gap:20px;}
    .menu-item {position:relative;}
    .menu a {color:white;text-decoration:none;padding:8px;}
    .dropdown {
        display:none;
        position:absolute;
        background:#334155;
        top:30px;
        min-width:150px;
    }
    .dropdown a {display:block;padding:8px;}
    .menu-item:hover .dropdown {display:block;}
    table {width:100%;margin-top:20px;}
    td,th {padding:10px;border-bottom:1px solid #444;}
    input,select,button {padding:8px;margin:5px;}
    </style>

    <div class="menu">

        <div class="menu-item">
            <a href="#">Estoque ▼</a>
            <div class="dropdown">
                <a href="/estoque">Produtos</a>
                <a href="/estoque_usuarios">Estoque Usuários</a>
            </div>
        </div>

        <div class="menu-item">
            <a href="#">Administração ▼</a>
            <div class="dropdown">
                <a href="/usuarios">Usuários</a>
            </div>
        </div>

        <a href="/dashboard">Dashboard</a>
        <a href="/logout" style="color:red;">Sair</a>

    </div>
    """

def container(c):
    return topo() + f"<div style='padding:20px'>{c}</div>"

# ================= LOGIN BONITO =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s",(user,))
        dado = cursor.fetchone()
        conn.close()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    <style>
    body {{
        margin:0;
        background:linear-gradient(135deg,#000,#1e293b);
        height:100vh;
        display:flex;
        justify-content:center;
        align-items:center;
        font-family:Arial;
        color:white;
    }}
    .login {{
        background:rgba(255,255,255,0.1);
        padding:40px;
        border-radius:20px;
        backdrop-filter: blur(20px);
        text-align:center;
    }}
    input {{
        display:block;
        width:200px;
        margin:10px auto;
        padding:10px;
        border:none;
        border-radius:10px;
    }}
    button {{
        padding:10px 20px;
        border:none;
        border-radius:10px;
        background:#3a86ff;
        color:white;
    }}
    </style>

    <div class="login">
        <h2>KBSISTEMAS</h2>
        <form method="POST">
            <input name="user" placeholder="Usuário">
            <input type="password" name="senha" placeholder="Senha">
            <button>LOGIN</button>
        </form>
        <p style="color:red;">{erro}</p>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return container(f"<h1>Bem-vindo {session['user']}</h1>")

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
        """,(request.form["produto"],request.form["qtd"],request.form["categoria"]))
        conn.commit()

    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela=""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"

    return container(f"""
    <h2>Produtos</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <select name="categoria">
            <option>Produto</option>
            <option>Material</option>
            <option>Ferramenta</option>
        </select>
        <button>Salvar</button>
    </form>

    <table>
        <tr><th>Produto</th><th>Qtd</th><th>Categoria</th></tr>
        {tabela}
    </table>
    """)

# ================= ESTOQUE USUÁRIOS =================
@app.route("/estoque_usuarios", methods=["GET","POST"])
def estoque_usuarios():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_user (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        produto TEXT,
        quantidade INTEGER
    )
    """)

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO estoque_user (usuario, produto, quantidade)
        VALUES (%s,%s,%s)
        """,(request.form["usuario"],request.form["produto"],request.form["qtd"]))
        conn.commit()

    cursor.execute("SELECT * FROM estoque_user")
    dados = cursor.fetchall()
    conn.close()

    tabela=""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"

    return container(f"""
    <h2>Estoque por Usuário</h2>

    <form method="POST">
        <input name="usuario" placeholder="Usuário">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <button>Lançar</button>
    </form>

    <table>
        <tr><th>Usuário</th><th>Produto</th><th>Qtd</th></tr>
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
        INSERT INTO usuarios VALUES (%s,%s,%s,%s)
        """,(request.form["user"],generate_password_hash(request.form["senha"]),request.form["cargo"],0))
        conn.commit()

    cursor.execute("SELECT usuario, cargo FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela=""
    for u,c in dados:
        tabela += f"<tr><td>{u}</td><td>{c}</td></tr>"

    return container(f"""
    <h2>Usuários</h2>

    <form method="POST">
        <input name="user">
        <input name="senha" type="password">
        <select name="cargo">
            <option>admin</option>
            <option>operador</option>
        </select>
        <button>Criar</button>
    </form>

    <table>
        <tr><th>Usuário</th><th>Cargo</th></tr>
        {tabela}
    </table>
    """)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
