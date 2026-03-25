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

    # 🔥 NOVO - estoque por usuário
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_usuarios (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        produto TEXT,
        quantidade INTEGER
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

# ================= TOPO =================
def topo():
    return f"""
    <div style="position:fixed;top:0;width:100%;height:60px;background:#0a192f;color:white;display:flex;align-items:center;justify-content:space-between;padding:0 20px;">
        <div style="font-weight:bold;color:#3a86ff;">⚡ KB Sistemas</div>
        <div>
            <a href="/dashboard">Dashboard</a>
            <a href="/estoque">Estoque</a>
            <a href="/estoque_usuarios">Estoque Usuários</a>
            <a href="/usuarios">Usuários</a>
            <a href="/saldo">Saldo</a>
            <a href="/logout" style="color:red;">Sair</a>
        </div>
    </div>
    """

def container(conteudo):
    return f"""
    {topo()}
    <div style="margin-top:70px;padding:20px;color:white;">
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

    return f"<h2>Login</h2><form method='POST'><input name='user'><input name='senha' type='password'><button>Entrar</button></form><p>{erro}</p>"

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

    # 🔒 Apenas admin adiciona
    if request.method == "POST" and session.get("cargo") == "admin":
        cursor.execute("""
        INSERT INTO estoque (produto, quantidade, categoria)
        VALUES (%s,%s,%s)
        """, (
            request.form["produto"],
            request.form["quantidade"],
            request.form["categoria"]
        ))
        conn.commit()

    cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for i,p,q,c in dados:
        excluir = ""
        if session.get("cargo") == "admin":
            excluir = f"<a href='/excluir/{i}'>❌</a>"

        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{c}</td><td>{excluir}</td></tr>"

    return container(f"""
    <h2>Estoque</h2>

    {"<form method='POST'>\
    <input name='produto'>\
    <input name='quantidade'>\
    <select name='categoria'>\
        <option>Produto</option>\
        <option>Material</option>\
        <option>Ferramenta</option>\
    </select>\
    <button>Adicionar</button>\
    </form>" if session.get("cargo") == "admin" else ""}

    <table border="1">
        <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ação</th></tr>
        {tabela}
    </table>
    """)

# ================= EXCLUIR =================
@app.route("/excluir/<int:id>")
def excluir(id):
    if session.get("cargo") != "admin":
        return "Não autorizado"

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM estoque WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/estoque")

# ================= ESTOQUE USUÁRIOS =================
@app.route("/estoque_usuarios", methods=["GET","POST"])
def estoque_usuarios():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # 🔥 TODOS podem lançar
    if request.method == "POST":
        cursor.execute("""
        INSERT INTO estoque_usuarios (usuario, produto, quantidade)
        VALUES (%s,%s,%s)
        """, (
            request.form["usuario"],
            request.form["produto"],
            request.form["quantidade"]
        ))
        conn.commit()

    cursor.execute("SELECT usuario, produto, quantidade FROM estoque_usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u,p,q in dados:
        tabela += f"<tr><td>{u}</td><td>{p}</td><td>{q}</td></tr>"

    return container(f"""
    <h2>Estoque por Usuário</h2>

    <form method="POST">
        <input name="usuario" placeholder="Usuário">
        <input name="produto" placeholder="Produto">
        <input name="quantidade" placeholder="Qtd">
        <button>Lançar</button>
    </form>

    <table border="1">
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
        INSERT INTO usuarios (usuario, senha, cargo, saldo, pode_estoque, pode_usuarios, online)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form["user"],
            generate_password_hash(request.form["senha"]),
            request.form["cargo"],
            0,1,1,0
        ))
        conn.commit()

    cursor.execute("SELECT usuario, cargo FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
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

    <table border="1">
        <tr><th>Usuário</th><th>Cargo</th></tr>
        {tabela}
    </table>
    """)

# ================= SALDO =================
@app.route("/saldo")
def saldo():
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
