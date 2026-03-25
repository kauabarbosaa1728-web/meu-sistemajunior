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

    cursor.execute("""CREATE TABLE IF NOT EXISTS correcoes (
        id SERIAL PRIMARY KEY,
        produto TEXT,
        quantidade INTEGER,
        motivo TEXT,
        usuario TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        <a href="/estoque" style="color:white;">Estoque</a> |
        <a href="/transferencia" style="color:white;">Transferência</a> |
        <a href="/correcao" style="color:white;">Correção</a> |
        <a href="/usuarios" style="color:white;">Usuários</a> |
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

            return redirect("/estoque")

        erro = "Login inválido"

    return f"""
    <style>
    body {{
        margin:0;
        font-family:Arial;
        background: linear-gradient(135deg, #020617, #0f172a);
        color:white;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
    }}
    .card {{
        background:#020617;
        padding:30px;
        border-radius:12px;
        width:320px;
        text-align:center;
        box-shadow:0 0 30px rgba(0,0,0,0.8);
    }}
    input {{
        width:100%;
        padding:10px;
        margin:8px 0;
        border:none;
        border-radius:6px;
    }}
    button {{
        width:100%;
        padding:10px;
        background:#3b82f6;
        border:none;
        border-radius:6px;
        color:white;
        cursor:pointer;
    }}
    </style>

    <div class="card">
        <h1>⚡ KBSISTEMAS</h1>
        <p style="font-size:12px;color:#94a3b8;">Sistema inteligente de controle</p>

        <form method="POST">
            <input name="user" placeholder="Usuário">
            <input name="senha" type="password" placeholder="Senha">
            <button>Entrar</button>
        </form>

        <p style="color:red;">{erro}</p>
        <p style="font-size:11px;color:#64748b;">Venha conhecer nosso serviço 🚀</p>
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

    cursor.execute("SELECT produto, quantidade, categoria FROM estoque")
    dados = cursor.fetchall()

    tabela = ""
    for p,q,c in dados:
        tabela += f"<tr><td>{p}</td><td>{q}</td><td>{c}</td></tr>"

    return container(f"""
    <h2>ESTOQUE</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="categoria" placeholder="Categoria">
        <button>Adicionar</button>
    </form>

    <table border="1">
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
    <h2>TRANSFERÊNCIA</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="destino" placeholder="Usuário destino">
        <button>Transferir</button>
    </form>
    """)

# ================= CORREÇÃO =================
@app.route("/correcao", methods=["GET","POST"])
def correcao():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO correcoes (produto, quantidade, motivo, usuario)
        VALUES (%s,%s,%s,%s)
        """, (
            request.form["produto"],
            request.form["qtd"],
            request.form["motivo"],
            session["user"]
        ))

        cursor.execute("""
        UPDATE estoque SET quantidade = quantidade - %s
        WHERE produto=%s
        """, (
            request.form["qtd"],
            request.form["produto"]
        ))

        conn.commit()

    return container("""
    <h2>CORREÇÃO</h2>

    <form method="POST">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="motivo" placeholder="Motivo">
        <button>Corrigir</button>
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
    <h2>USUÁRIOS</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário">
        <input name="senha" placeholder="Senha">
        <select name="cargo">
            <option value="admin">Admin</option>
            <option value="operador">Operador</option>
        </select>
        <button>Criar</button>
    </form>

    <table border="1">
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

# ================= ALTERAR SENHA =================
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
