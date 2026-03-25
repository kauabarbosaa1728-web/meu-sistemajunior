from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

app = Flask(__name__)
app.secret_key = "segredo123"

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

    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
        senha TEXT,
        cargo TEXT,
        saldo INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque_user (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        produto TEXT,
        quantidade INTEGER
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS correcoes (
        id SERIAL PRIMARY KEY,
        tipo TEXT,
        nome TEXT,
        quantidade INTEGER,
        motivo TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS transferencias (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        origem TEXT,
        destino TEXT,
        usuario TEXT,
        status TEXT DEFAULT 'Pendente',
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS historico (
        id SERIAL PRIMARY KEY,
        acao TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

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
        cursor.execute(
            "INSERT INTO usuarios VALUES (%s,%s,%s,%s)",
            ("admin", generate_password_hash("123"), "admin", 0)
        )

    conn.commit()
    conn.close()

criar_admin()

# ================= HISTÓRICO =================
def registrar(msg):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO historico (acao, usuario) VALUES (%s,%s)",
                   (msg, session.get("user")))
    conn.commit()
    conn.close()

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
    input,select,button {padding:8px;margin:5px;}
    </style>

    <div class="menu">
        <div class="menu-item">
            <a href="#">Estoque ▼</a>
            <div class="dropdown">
                <a href="/estoque">Produtos</a>
                <a href="/estoque_usuarios">Estoque Usuários</a>
                <a href="/correcao">Correções</a>
                <a href="/transferencia">Transferência</a>
                <a href="/historico">Histórico</a>
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
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s",(request.form.get("user"),))
        dado = cursor.fetchone()
        conn.close()

        if dado and check_password_hash(dado[0], request.form.get("senha")):
            session["user"] = request.form.get("user")
            session["cargo"] = dado[1]
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""<form method="POST">
    <input name="user"><br>
    <input name="senha"><br>
    <button>Login</button>
    <p>{erro}</p>
    </form>"""

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

    busca = request.args.get("busca")

    if request.method == "POST":
        if session.get("cargo") == "usuario":
            return container("Sem permissão")

        produto = request.form.get("produto")
        qtd = request.form.get("qtd")

        try:
            qtd = int(qtd)
        except:
            return container("Quantidade inválida")

        cursor.execute("INSERT INTO estoque (produto, quantidade, categoria) VALUES (%s,%s,%s)",
                       (produto,qtd,request.form.get("categoria")))

        registrar(f"Adicionou {produto} ({qtd})")
        conn.commit()

    if busca:
        cursor.execute("SELECT * FROM estoque WHERE produto ILIKE %s",(f"%{busca}%",))
    else:
        cursor.execute("SELECT * FROM estoque")

    dados = cursor.fetchall()
    conn.close()

    tabela="".join([f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>" for d in dados])

    return container(f"""
    <h2>Produtos</h2>
    <form>
        <input name="busca" placeholder="Buscar produto">
        <button>Buscar</button>
    </form>

    <form method="POST">
        <input name="produto">
        <input name="qtd">
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

# ================= CORREÇÃO =================
@app.route("/correcao", methods=["GET","POST"])
def correcao():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("INSERT INTO correcoes (tipo,nome,quantidade,motivo,usuario) VALUES (%s,%s,%s,%s,%s)",
                       (request.form.get("tipo"),request.form.get("nome"),request.form.get("quantidade"),
                        request.form.get("motivo"),session["user"]))

        registrar("Correção realizada")
        conn.commit()

    cursor.execute("SELECT * FROM correcoes ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()

    tabela="".join([f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>" for d in dados])

    return container(f"""
    <h2>Correções</h2>
    <form method="POST">
        <input name="tipo">
        <input name="nome">
        <input name="quantidade">
        <input name="motivo">
        <button>Salvar</button>
    </form>
    <table>{tabela}</table>
    """)

# ================= TRANSFERÊNCIA =================
@app.route("/transferencia", methods=["GET","POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""INSERT INTO transferencias 
        (produto,quantidade,origem,destino,usuario)
        VALUES (%s,%s,%s,%s,%s)""",
        (request.form.get("produto"),
         int(request.form.get("qtd")),
         request.form.get("origem"),
         request.form.get("destino"),
         session["user"]))

        registrar("Transferência realizada")
        conn.commit()

    cursor.execute("SELECT * FROM transferencias ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()

    tabela="".join([f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>" for d in dados])

    return container(f"""
    <h2>Transferência</h2>
    <form method="POST">
        <input name="produto">
        <input name="qtd">
        <input name="origem">
        <input name="destino">
        <button>Enviar</button>
    </form>
    <table>{tabela}</table>
    """)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
