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
        cargo TEXT
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
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", ("admin",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios VALUES (%s,%s,%s)",
            ("admin", generate_password_hash("123"), "admin")
        )

    conn.commit()
    conn.close()

criar_admin()

# ================= MENU =================
def topo():
    return """
    <div style="background:#1e293b;padding:10px;">
        <a href="/estoque">Produtos</a> |
        <a href="/estoque_usuarios">Estoque Usuários</a> |
        <a href="/correcao">Correções</a> |
        <a href="/transferencia">Transferência</a> |
        <a href="/historico">Histórico</a> |
        <a href="/usuarios">Usuários</a> |
        <a href="/logout">Sair</a>
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
                       (request.form.get("user"),))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], request.form.get("senha")):
            session["user"] = request.form.get("user")
            session["cargo"] = dado[1]
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""
    <form method="POST">
        <input name="user">
        <input name="senha" type="password">
        <button>Login</button>
    </form>
    {erro}
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    return container(f"Bem vindo {session.get('user')}")

# ================= ESTOQUE =================
@app.route("/estoque", methods=["GET","POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        try:
            cursor.execute(
                "INSERT INTO estoque (produto, quantidade, categoria) VALUES (%s,%s,%s)",
                (request.form["produto"], int(request.form["qtd"]), request.form["categoria"])
            )

            cursor.execute(
                "INSERT INTO historico (acao, usuario) VALUES (%s,%s)",
                (f"Adicionou {request.form['produto']}", session["user"])
            )

            conn.commit()
        except Exception as e:
            print(e)

    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()

    tabela = ""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"

    return container(f"""
    <h2>Produtos</h2>
    <form method="POST">
        <input name="produto">
        <input name="qtd">
        <input name="categoria">
        <button>Salvar</button>
    </form>
    <table>
    {tabela}
    </table>
    """)

# ================= ESTOQUE USUÁRIOS =================
@app.route("/estoque_usuarios", methods=["GET","POST"])
def estoque_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO estoque_user (usuario, produto, quantidade)
        VALUES (%s,%s,%s)
        """,(request.form["usuario"],request.form["produto"],request.form["qtd"]))

        conn.commit()

    cursor.execute("SELECT * FROM estoque_user")
    dados = cursor.fetchall()

    tabela=""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"

    return container(f"<table>{tabela}</table>")

# ================= CORREÇÃO =================
@app.route("/correcao", methods=["GET","POST"])
def correcao():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO correcoes (tipo, nome, quantidade, motivo, usuario)
        VALUES (%s,%s,%s,%s,%s)
        """,(request.form["tipo"],request.form["nome"],
             request.form["quantidade"],request.form["motivo"],
             session["user"]))

        cursor.execute(
            "INSERT INTO historico (acao, usuario) VALUES (%s,%s)",
            (f"Correção {request.form['nome']}", session["user"])
        )

        conn.commit()

    return container("Correção OK")

# ================= TRANSFERÊNCIA =================
@app.route("/transferencia", methods=["GET","POST"])
def transferencia():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
        VALUES (%s,%s,%s,%s,%s)
        """,(request.form["produto"],request.form["qtd"],
             request.form["origem"],request.form["destino"],
             session["user"]))

        conn.commit()

    return container("Transferência OK")

# ================= HISTÓRICO =================
@app.route("/historico")
def historico():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM historico ORDER BY id DESC")
    dados = cursor.fetchall()

    tabela=""
    for d in dados:
        tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"

    return container(f"<table>{tabela}</table>")

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET","POST"])
def usuarios():
    if session.get("cargo") != "admin":
        return container("SEM PERMISSÃO")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute(
            "INSERT INTO usuarios VALUES (%s,%s,%s)",
            (request.form["user"], generate_password_hash(request.form["senha"]), request.form["cargo"])
        )
        conn.commit()

    return container("""
    <form method="POST">
        <input name="user">
        <input name="senha">
        <select name="cargo">
            <option>admin</option>
            <option>operador</option>
        </select>
        <button>Criar</button>
    </form>
    """)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
