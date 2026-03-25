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

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque_user (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        produto TEXT,
        quantidade INTEGER
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS transferencias (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        destino TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

criar_banco()

# ================= ADMIN =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", ("kaua.barbosaa1728@gmail.com",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios VALUES (%s,%s,%s,%s)",
            ("kaua.barbosaa1728@gmail.com", generate_password_hash("997401054"), "admin", 0)
        )
    else:
        cursor.execute(
            "UPDATE usuarios SET senha=%s WHERE usuario=%s",
            (generate_password_hash("997401054"), "kaua.barbosaa1728@gmail.com")
        )

    conn.commit()
    conn.close()

criar_admin()

# ================= MENU =================
def topo():
    return """
    <div style="background:#0f172a;padding:15px;color:white;">
        <b style="font-size:18px;">⚡ KBSISTEMAS</b> |
        <a href="/dashboard" style="color:white;">Dashboard</a> |
        <a href="/estoque" style="color:white;">Estoque</a> |
        <a href="/estoque_usuarios" style="color:white;">Estoque Usuários</a> |
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

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM estoque")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM estoque")
    total_qtd = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transferencias")
    total_transf = cursor.fetchone()[0]

    conn.close()

    return container(f"""
    <h2>📊 DASHBOARD</h2>

    <div style="display:flex;gap:20px;flex-wrap:wrap;">
        <div style="background:#020617;padding:20px;border-radius:10px;">
            <h3>📦 Produtos</h3>
            <h1>{total_produtos}</h1>
        </div>

        <div style="background:#020617;padding:20px;border-radius:10px;">
            <h3>📊 Quantidade</h3>
            <h1>{total_qtd}</h1>
        </div>

        <div style="background:#020617;padding:20px;border-radius:10px;">
            <h3>👤 Usuários</h3>
            <h1>{total_users}</h1>
        </div>

        <div style="background:#020617;padding:20px;border-radius:10px;">
            <h3>🔄 Transferências</h3>
            <h1>{total_transf}</h1>
        </div>
    </div>
    """)

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s",
                       (request.form["user"],))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], request.form["senha"]):
            session["user"] = request.form["user"]
            session["cargo"] = dado[1]

            cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s",
                           (request.form["user"],))
            conn.commit()
            conn.close()

            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    <div style="text-align:center;margin-top:100px;">
        <h1>⚡ KBSISTEMAS</h1>
        <form method="POST">
            <input name="user" placeholder="Usuário"><br>
            <input name="senha" type="password" placeholder="Senha"><br>
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
        cursor.execute(
            "INSERT INTO estoque (produto, quantidade, categoria) VALUES (%s,%s,%s)",
            (request.form["produto"], request.form["qtd"], request.form["categoria"])
        )
        conn.commit()

    cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque")
    dados = cursor.fetchall()

    tabela = ""
    for i,p,q,c in dados:
        tabela += f"""
        <tr>
            <td>{p}</td>
            <td>{q}</td>
            <td>{c}</td>
            <td><a href="/remover_estoque/{i}">❌ Remover</a></td>
        </tr>
        """

    return container(f"""
    <h2>📦 ESTOQUE</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="categoria" placeholder="Categoria">
        <button>Adicionar</button>
    </form>

    <table>
        <tr><th>Produto</th><th>Qtd</th><th>Categoria</th><th></th></tr>
        {tabela}
    </table>
    """)

# ================= REMOVER ESTOQUE =================
@app.route("/remover_estoque/<int:id>")
def remover_estoque(id):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/estoque")

# ================= ESTOQUE USUÁRIOS =================
@app.route("/estoque_usuarios")
def estoque_usuarios():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, usuario, produto, quantidade FROM estoque_user")
    dados = cursor.fetchall()

    tabela = ""
    for i,u,p,q in dados:
        tabela += f"""
        <tr>
            <td>{u}</td>
            <td>{p}</td>
            <td>{q}</td>
            <td><a href="/remover_user/{i}">❌ Remover</a></td>
        </tr>
        """

    conn.close()

    return container(f"""
    <h2>👤 ESTOQUE DOS USUÁRIOS</h2>

    <table>
        <tr><th>Usuário</th><th>Produto</th><th>Qtd</th><th></th></tr>
        {tabela}
    </table>
    """)

# ================= REMOVER USER =================
@app.route("/remover_user/<int:id>")
def remover_user(id):
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque_user WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/estoque_usuarios")

# ================= TRANSFERÊNCIA =================
@app.route("/transferencia", methods=["GET","POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO transferencias (produto, quantidade, destino, usuario)
        VALUES (%s,%s,%s,%s)
        """, (
            request.form["produto"],
            request.form["qtd"],
            request.form["destino"],
            session["user"]
        ))

        cursor.execute("""
        INSERT INTO estoque_user (usuario, produto, quantidade)
        VALUES (%s,%s,%s)
        """, (
            request.form["destino"],
            request.form["produto"],
            request.form["qtd"]
        ))

        conn.commit()

    return container("""
    <h2>🔄 TRANSFERÊNCIA</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="destino" placeholder="Usuário destino">
        <button>Transferir</button>
    </form>
    """)

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if session.get("cargo") != "admin":
        return container("SEM PERMISSÃO")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute(
            "INSERT INTO usuarios VALUES (%s,%s,%s,%s)",
            (request.form["user"],
             generate_password_hash(request.form["senha"]),
             request.form["cargo"],
             0)
        )
        conn.commit()

    cursor.execute("SELECT usuario, cargo, online FROM usuarios")
    dados = cursor.fetchall()

    tabela = ""
    for u,c,o in dados:
        status = "🟢 Online" if o == 1 else "🔴 Offline"
        tabela += f"""
        <tr>
            <td>{u}</td>
            <td>{c}</td>
            <td>{status}</td>
            <td><a href="/excluir/{u}">Excluir</a></td>
            <td><a href="/senha/{u}">Senha</a></td>
        </tr>
        """

    return container(f"""
    <h2>👤 USUÁRIOS</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário">
        <input name="senha" placeholder="Senha">
        <select name="cargo">
            <option value="admin">Admin</option>
            <option value="operador">Operador</option>
        </select>
        <button>Criar</button>
    </form>

    <table>
        <tr><th>Usuário</th><th>Cargo</th><th>Status</th><th></th><th></th></tr>
        {tabela}
    </table>
    """)

# ================= EXCLUIR =================
@app.route("/excluir/<usuario>")
def excluir(usuario):
    if session.get("cargo") != "admin":
        return "Sem permissão"

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario,))
    conn.commit()
    conn.close()

    return redirect("/usuarios")

# ================= SENHA =================
@app.route("/senha/<usuario>", methods=["GET","POST"])
def senha(usuario):
    if session.get("cargo") != "admin":
        return "Sem permissão"

    if request.method == "POST":
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE usuarios SET senha=%s WHERE usuario=%s",
            (generate_password_hash(request.form["nova"]), usuario)
        )
        conn.commit()
        conn.close()

        return redirect("/usuarios")

    return f"""
    <h3>Alterar senha de {usuario}</h3>
    <form method="POST">
        <input name="nova" placeholder="Nova senha">
        <button>Salvar</button>
    </form>
    """

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
    app.run(debug=True)
