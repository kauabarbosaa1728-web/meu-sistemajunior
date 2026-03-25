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

    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
        senha TEXT,
        cargo TEXT,
        online INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        categoria TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS transferencias (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        origem TEXT,
        destino TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

# ================= TOPO =================
def topo():
    return """
    <div style="background:#020617;padding:15px;color:white;">
        <b style="font-size:18px;">⚡ KBSISTEMAS</b> |
        <a href="/estoque" style="color:white;">Estoque</a> |
        <a href="/transferencia" style="color:white;">Transferência</a> |
        <a href="/usuarios" style="color:white;">Usuários</a> |
        <a href="/logout" style="color:red;">Sair</a>
    </div>
    """

# ================= CONTAINER =================
def container(c):
    return topo() + f"""
    <style>
    body {{
        margin:0;
        font-family:Arial;
        background: url('https://images.unsplash.com/photo-1518770660439-4636190af475') no-repeat center center fixed;
        background-size: cover;
        color:white;
    }}

    .overlay {{
        background: rgba(2,6,23,0.85);
        min-height:100vh;
        padding:20px;
    }}

    input, button {{
        padding:10px;
        margin:5px 0;
        border-radius:6px;
        border:none;
    }}

    button {{
        background:#3b82f6;
        color:white;
        cursor:pointer;
    }}

    table {{
        width:100%;
        background:#020617;
        border-collapse:collapse;
        margin-top:15px;
    }}

    th, td {{
        padding:10px;
        border:1px solid #1e293b;
    }}
    </style>

    <div class="overlay">
        {c}
    </div>
    """

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (request.form["user"],))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], request.form["senha"]):
            session["user"] = user[0]
            session["cargo"] = user[2]

            cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (user[0],))
            conn.commit()
            conn.close()

            return redirect("/estoque")
        else:
            erro = "Login inválido"

    return f"""
    <div style="padding:50px">
        <h2>Login</h2>
        <form method="POST">
            <input name="user" placeholder="Usuário"><br>
            <input name="senha" placeholder="Senha" type="password"><br>
            <button>Entrar</button>
        </form>

        <p style="color:red;">{erro}</p>
    </div>
    """

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
            request.form["qtd"],
            request.form["categoria"]
        ))
        conn.commit()

    # EXCLUIR PRODUTO (só admin)
    if request.args.get("del") and session.get("cargo") == "admin":
        cursor.execute("DELETE FROM estoque WHERE id=%s", (request.args.get("del"),))
        conn.commit()
        return redirect("/estoque")

    cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque")
    dados = cursor.fetchall()

    tabela = ""
    for i, p, q, c in dados:
        botao = ""
        if session.get("cargo") == "admin":
            botao = f"<a href='/estoque?del={i}'><button>Excluir</button></a>"

        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{c}</td><td>{botao}</td></tr>"

    return container(f"""
    <h2>📦 ESTOQUE</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="categoria" placeholder="Categoria">
        <button>Adicionar</button>
    </form>

    <table>
        <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th>Ação</th></tr>
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
        cursor.execute("""
        INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
        VALUES (%s,%s,%s,%s,%s)
        """, (
            request.form["produto"],
            request.form["qtd"],
            request.form["origem"],
            request.form["destino"],
            session["user"]
        ))
        conn.commit()

    return container("""
    <h2>🔄 TRANSFERÊNCIA</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="origem" placeholder="Origem">
        <input name="destino" placeholder="Destino">
        <button>Transferir</button>
    </form>
    """)

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if session.get("cargo") != "admin":
        return "Sem permissão"

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO usuarios (usuario, senha, cargo)
        VALUES (%s,%s,%s)
        """, (
            request.form["user"],
            generate_password_hash(request.form["senha"]),
            request.form["cargo"]
        ))
        conn.commit()

    # EXCLUIR USUARIO
    if request.args.get("del"):
        cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (request.args.get("del"),))
        conn.commit()
        return redirect("/usuarios")

    cursor.execute("SELECT usuario, cargo, online FROM usuarios")
    dados = cursor.fetchall()

    tabela = ""
    for u, c, o in dados:
        status = "🟢" if o else "🔴"
        tabela += f"<tr><td>{u}</td><td>{c}</td><td>{status}</td><td><a href='/usuarios?del={u}'><button>Excluir</button></a></td></tr>"

    return container(f"""
    <h2>👤 USUÁRIOS</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário">
        <input name="senha" placeholder="Senha">
        
        <select name="cargo">
            <option value="operador">Operador</option>
            <option value="admin">Admin</option>
        </select>

        <button>Criar</button>
    </form>

    <table>
        <tr><th>Usuário</th><th>Cargo</th><th>Status</th><th>Ação</th></tr>
        {tabela}
    </table>
    """)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    if "user" in session:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("UPDATE usuarios SET online=0 WHERE usuario=%s",
                       (session["user"],))
        conn.commit()
        conn.close()

    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
