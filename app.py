from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

app = Flask(__name__)
app.secret_key = "segredo123"
app.config['PROPAGATE_EXCEPTIONS'] = True

# ================= CONEXÃO =================
def conectar():
    try:
        return psycopg2.connect(
            host="ep-calm-moon-acucwei3-pooler.sa-east-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_zGebRqQWoB06",
            port="5432",
            sslmode="require"
        )
    except Exception as e:
        print("ERRO BANCO:", e)
        return None

# ================= BANCO =================
def criar_banco():
    conn = conectar()
    if not conn:
        return

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
        senha TEXT,
        cargo TEXT,
        saldo INTEGER DEFAULT 0,
        online BOOLEAN DEFAULT FALSE
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_user (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        produto TEXT,
        quantidade INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS correcoes (
        id SERIAL PRIMARY KEY,
        tipo TEXT,
        nome TEXT,
        quantidade INTEGER,
        motivo TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transferencias (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        origem TEXT,
        destino TEXT,
        usuario TEXT,
        status TEXT DEFAULT 'Pendente'
    )
    """)

    conn.commit()
    conn.close()

criar_banco()

# ================= ADMIN =================
def criar_admin():
    conn = conectar()
    if not conn:
        return

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", ("admin",))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO usuarios VALUES (%s,%s,%s,%s,%s)
        """, ("admin", generate_password_hash("123"), "admin", 0, False))

    conn.commit()
    conn.close()

criar_admin()

# ================= MENU =================
def topo():
    return """
    <style>
    body {margin:0;background:#0f172a;color:white;font-family:Arial;}
    .menu {background:#1e293b;padding:10px;display:flex;gap:20px;}
    .menu-item {position:relative;}
    .menu a {color:white;text-decoration:none;padding:8px;}
    .dropdown {display:none;position:absolute;background:#334155;top:30px;}
    .dropdown a {display:block;padding:8px;}
    .menu-item:hover .dropdown {display:block;}
    table {width:100%;margin-top:20px;}
    td,th {padding:10px;border-bottom:1px solid #444;}
    input,button,select {padding:8px;margin:5px;}
    </style>

    <div class="menu">
        <div class="menu-item">
            <a href="#">Estoque ▼</a>
            <div class="dropdown">
                <a href="/estoque">Produtos</a>
                <a href="/estoque_usuarios">Estoque Usuários</a>
                <a href="/correcao">Correções</a>
                <a href="/transferencia">Transferência</a>
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

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        user = request.form.get("user")
        senha = request.form.get("senha")

        conn = conectar()
        if not conn:
            return "Erro de conexão com banco"

        cursor = conn.cursor()
        cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s",(user,))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]

            cursor.execute("UPDATE usuarios SET online=TRUE WHERE usuario=%s",(user,))
            conn.commit()
            conn.close()
            return redirect("/dashboard")

        conn.close()
        erro = "Login inválido"

    return f"""
    <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#000;">
    <div style="background:#1e293b;padding:40px;border-radius:20px;text-align:center;">
        <h2>KBSISTEMAS</h2>
        <form method="POST">
            <input name="user" placeholder="Usuário"><br><br>
            <input type="password" name="senha" placeholder="Senha"><br><br>
            <button>LOGIN</button>
        </form>
        <p style="color:red;">{erro}</p>
    </div>
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
    if not conn:
        return container("<h3>Erro no banco</h3>")

    cursor = conn.cursor()

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")

        try:
            qtd = int(qtd)
        except:
            return container("<h3>Quantidade inválida</h3>")

        cursor.execute("""
        INSERT INTO estoque (produto, quantidade, categoria)
        VALUES (%s,%s,%s)
        """,(produto,qtd,categoria))
        conn.commit()
        return redirect("/estoque")

    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela=""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"

    return container(f"""
    <h2>Produtos</h2>
    <form method="POST">
        <input name="produto" placeholder="Nome do produto">
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

# ================= TRANSFERÊNCIA =================
@app.route("/transferencia", methods=["GET","POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    if not conn:
        return container("<h3>Erro no banco</h3>")

    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
        VALUES (%s,%s,%s,%s,%s)
        """,(
            request.form.get("produto"),
            request.form.get("qtd"),
            request.form.get("origem"),
            request.form.get("destino"),
            session["user"]
        ))
        conn.commit()

    cursor.execute("SELECT * FROM transferencias")
    dados = cursor.fetchall()
    conn.close()

    tabela=""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td><td>{d[5]}</td><td>{d[6]}</td></tr>"

    return container(f"""
    <h2>Transferência</h2>
    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="origem" placeholder="Origem">
        <input name="destino" placeholder="Destino">
        <button>Enviar</button>
    </form>
    <table>
        <tr><th>Produto</th><th>Qtd</th><th>Origem</th><th>Destino</th><th>Usuário</th><th>Status</th></tr>
        {tabela}
    </table>
    """)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    if "user" in session:
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET online=FALSE WHERE usuario=%s",(session["user"],))
            conn.commit()
            conn.close()

    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
