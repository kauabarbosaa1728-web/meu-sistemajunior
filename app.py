from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= BANCO =================
def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # 🔥 atualizado (novos campos)
    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        user TEXT,
        senha TEXT,
        cargo TEXT,
        pode_estoque INTEGER DEFAULT 1,
        pode_historico INTEGER DEFAULT 1,
        pode_usuarios INTEGER DEFAULT 0,
        online INTEGER DEFAULT 0,
        saldo INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS saldo_historico (
        usuario TEXT,
        valor INTEGER,
        descricao TEXT,
        quem_lancou TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS estoque (
        produto TEXT, quantidade INTEGER, categoria TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
        produto TEXT,
        quantidade INTEGER,
        tipo TEXT,
        usuario TEXT,
        local_saida TEXT,
        destino TEXT,
        observacao TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

criar_banco()

# ================= ADMIN =================
def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    if not cursor.execute("SELECT * FROM usuarios WHERE user=?", ("admin",)).fetchone():
        cursor.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?)",
                       ("admin", generate_password_hash("123"), "admin", 1, 1, 1, 0, 0))

    conn.commit()
    conn.close()

criar_admin()

# ================= PERMISSÃO =================
def verificar_permissao(tipo):
    if "user" not in session:
        return False

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"SELECT {tipo} FROM usuarios WHERE user=?", (session["user"],))
    dado = cursor.fetchone()
    conn.close()

    return dado and dado[0] == 1

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = ""
    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT senha, cargo FROM usuarios WHERE user=?", (user,))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]

            # 🟢 ONLINE
            cursor.execute("UPDATE usuarios SET online=1 WHERE user=?", (user,))
            conn.commit()
            conn.close()

            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    {estilo()}
    <body style="display:flex;justify-content:center;align-items:center;height:100vh;">
    <div class="card" style="width:320px;text-align:center;">
        <h1>KBSISTEMAS</h1>
        <form method="POST">
            <input name="user" placeholder="Usuário"><br>
            <input name="senha" type="password" placeholder="Senha"><br>
            <button>Entrar</button>
            <p style="color:red;">{erro}</p>
        </form>
    </div>
    </body>
    """

# ================= MENU =================
def layout():
    return """
    <div class="card">
        <a href="/dashboard">Dashboard</a> |
        <a href="/estoque">Estoque</a> |
        <a href="/historico">Histórico</a> |
        <a href="/usuarios">Usuários</a> |
        <a href="/saldo">Meu Saldo</a> |
        <a href="/logout">Sair</a>
    </div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return f"{estilo()}{layout()}<div class='container'><div class='card'><h2>Bem-vindo {session['user']}</h2></div></div>"

# ================= SALDO =================
@app.route("/saldo")
def saldo():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT saldo FROM usuarios WHERE user=?", (session["user"],))
    saldo = cursor.fetchone()[0]

    conn.close()

    return f"""
    {estilo()}{layout()}
    <div class="container">
        <div class="card">
            <h2>Seu saldo: {saldo}</h2>
            <a href="/extrato/{session['user']}">Ver extrato</a>
        </div>
    </div>
    """

# ================= EXTRATO =================
@app.route("/extrato/<usuario>")
def extrato(usuario):
    if "user" not in session:
        return redirect("/")

    if session["user"] != usuario and session["cargo"] != "admin":
        return "Não autorizado. Falar com o administrador."

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM saldo_historico WHERE usuario=? ORDER BY data DESC", (usuario,))
    dados = cursor.fetchall()

    conn.close()

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>"

    return f"""
    {estilo()}{layout()}
    <div class="container">
        <div class="card">
            <h2>Extrato de {usuario}</h2>
            <table>
                <tr><th>Valor</th><th>Descrição</th><th>Quem lançou</th><th>Data</th></tr>
                {tabela}
            </table>
        </div>
    </div>
    """

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if "user" not in session:
        return redirect("/")

    if not verificar_permissao("pode_usuarios"):
        return "Não autorizado. Falar com o administrador."

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?)", (
            request.form["user"],
            generate_password_hash(request.form["senha"]),
            request.form["cargo"],
            1 if request.form.get("estoque") else 0,
            1 if request.form.get("historico") else 0,
            1 if request.form.get("usuarios") else 0,
            0,
            0
        ))
        conn.commit()

    cursor.execute("SELECT user, cargo, online FROM usuarios")
    dados = cursor.fetchall()
    conn.close()

    tabela = ""
    for u, c, o in dados:
        status = "🟢 Online" if o == 1 else "🔴 Offline"
        tabela += f"<tr><td>{u}</td><td>{c}</td><td>{status}</td><td><a href='/ver_saldo/{u}'>Saldo</a></td></tr>"

    return f"""
    {estilo()}{layout()}
    <div class="container">

    <div class="card">
        <h2>Criar Usuário</h2>
        <form method="POST">
            <input name="user" placeholder="Usuário">
            <input name="senha" type="password" placeholder="Senha">

            <select name="cargo">
                <option value="admin">Admin</option>
                <option value="operador">Operador</option>
            </select><br>

            <label><input type="checkbox" name="estoque"> Estoque</label><br>
            <label><input type="checkbox" name="historico"> Histórico</label><br>
            <label><input type="checkbox" name="usuarios"> Usuários</label><br>

            <button>Criar</button>
        </form>
    </div>

    <div class="card">
        <table>
            <tr><th>Usuário</th><th>Cargo</th><th>Status</th><th>Saldo</th></tr>
            {tabela}
        </table>
    </div>

    </div>
    """

# ================= VER SALDO =================
@app.route("/ver_saldo/<usuario>")
def ver_saldo(usuario):
    if session.get("cargo") != "admin":
        return "Não autorizado. Falar com o administrador."

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT saldo FROM usuarios WHERE user=?", (usuario,))
    saldo = cursor.fetchone()[0]

    conn.close()

    return f"""
    {estilo()}{layout()}
    <div class="container">
        <div class="card">
            <h2>Saldo de {usuario}: {saldo}</h2>
            <a href="/extrato/{usuario}">Ver extrato</a><br><br>
            <a href="/lancar/{usuario}">Lançar saldo</a>
        </div>
    </div>
    """

# ================= LANÇAR =================
@app.route("/lancar/<usuario>", methods=["GET","POST"])
def lancar(usuario):
    if session.get("cargo") != "admin":
        return "Não autorizado. Falar com o administrador."

    if request.method == "POST":
        valor = int(request.form["valor"])
        desc = request.form["desc"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE user=?", (valor, usuario))

        cursor.execute("INSERT INTO saldo_historico VALUES (?,?,?,?)",
                       (usuario, valor, desc, session["user"]))

        conn.commit()
        conn.close()

        return redirect(f"/ver_saldo/{usuario}")

    return f"""
    {estilo()}{layout()}
    <div class="container">
        <div class="card">
            <h2>Lançar saldo para {usuario}</h2>
            <form method="POST">
                <input name="valor" type="number" placeholder="Valor">
                <input name="desc" placeholder="Descrição">
                <button>Lançar</button>
            </form>
        </div>
    </div>
    """

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    if "user" in session:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET online=0 WHERE user=?", (session["user"],))
        conn.commit()
        conn.close()

    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
