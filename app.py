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

    # 🔥 NOVO
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transferencias (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        origem TEXT,
        destino TEXT,
        usuario TEXT,
        status TEXT DEFAULT 'Pendente',
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# ================= MENU =================
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
    <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#000;">
    <div style="background:#1e293b;padding:40px;border-radius:20px;text-align:center;">
        <h2>KBSISTEMAS</h2>
        <form method="POST">
            <input name="user"><br><br>
            <input type="password" name="senha"><br><br>
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
    cursor = conn.cursor()

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")

        if not produto or not qtd:
            return container("<h3>Preencha produto e quantidade</h3>")

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

# ================= TRANSFERÊNCIA =================
@app.route("/transferencia", methods=["GET","POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        try:
            qtd = int(request.form.get("qtd"))
        except:
            return container("<h3>Quantidade inválida</h3>")

        cursor.execute("""
        INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
        VALUES (%s,%s,%s,%s,%s)
        """,(
            request.form.get("produto"),
            qtd,
            request.form.get("origem"),
            request.form.get("destino"),
            session["user"]
        ))
        conn.commit()

    if request.args.get("aprovar"):
        cursor.execute("""
        UPDATE transferencias SET status='Aprovado' WHERE id=%s
        """,(request.args.get("aprovar"),))
        conn.commit()

    cursor.execute("SELECT * FROM transferencias ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()

    tabela=""
    for d in dados:
        btn=""
        if d[6] == "Pendente":
            btn = f"<a href='/transferencia?aprovar={d[0]}'>Aprovar</a>"

        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td><td>{d[5]}</td><td>{d[6]}</td><td>{btn}</td></tr>"

    return container(f"""
    <h2>Transferências</h2>

    <form method="POST">
        <input name="produto">
        <input name="qtd">
        <input name="origem">
        <input name="destino">
        <button>Enviar</button>
    </form>

    <table>
        <tr><th>Produto</th><th>Qtd</th><th>Origem</th><th>Destino</th><th>Usuário</th><th>Status</th><th>Ação</th></tr>
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
