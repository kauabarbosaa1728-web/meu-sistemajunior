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

# ================= MENU =================
def topo():
    return """
    <div>
        <a href="/estoque">Produtos</a> |
        <a href="/estoque_usuarios">Estoque Usuários</a> |
        <a href="/correcao">Correções</a> |
        <a href="/transferencia">Transferência</a> |
        <a href="/historico">Histórico</a> |
        <a href="/usuarios">Usuários</a> |
        <a href="/logout">Sair</a>
    </div><hr>
    """

def container(c):
    return topo() + c

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT senha,cargo FROM usuarios WHERE usuario=%s",
                       (request.form.get("user"),))
        dado = cursor.fetchone()

        if dado and check_password_hash(dado[0], request.form.get("senha")):
            session["user"] = request.form.get("user")
            session["cargo"] = dado[1]
            return redirect("/dashboard")

    return """
    <form method="POST">
    <input name="user" placeholder="usuario">
    <input name="senha" type="password">
    <button>login</button>
    </form>
    """

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    return container(f"Bem vindo {session.get('user')}")

# ================= ESTOQUE =================
@app.route("/estoque", methods=["GET","POST"])
def estoque():
    try:
        conn = conectar()
        cursor = conn.cursor()

        if request.method == "POST":
            produto = request.form.get("produto")
            qtd = request.form.get("qtd")
            categoria = request.form.get("categoria")

            if produto and qtd:
                cursor.execute(
                    "INSERT INTO estoque (produto,quantidade,categoria) VALUES (%s,%s,%s)",
                    (produto,int(qtd),categoria))
                conn.commit()

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
        <table>{tabela}</table>
        """)

    except Exception as e:
        print("ERRO:", e)
        return "erro estoque"

# ================= TRANSFERENCIA =================
@app.route("/transferencia", methods=["GET","POST"])
def transferencia():
    try:
        conn = conectar()
        cursor = conn.cursor()

        if request.method == "POST":
            cursor.execute("""
            INSERT INTO transferencias (produto,quantidade,origem,destino,usuario)
            VALUES (%s,%s,%s,%s,%s)
            """,(
                request.form.get("produto"),
                int(request.form.get("qtd")),
                request.form.get("origem"),
                request.form.get("destino"),
                session.get("user")
            ))
            conn.commit()

        cursor.execute("SELECT * FROM transferencias")
        dados = cursor.fetchall()

        tabela=""
        for d in dados:
            tabela+=f"<tr><td>{d[1]}</td><td>{d[2]}</td></tr>"

        return container(f"<h2>Transferencia</h2><table>{tabela}</table>")

    except Exception as e:
        print("ERRO TRANSF:", e)
        return "erro transferencia"

# ================= CORRECAO =================
@app.route("/correcao")
def correcao():
    return container("Correção funcionando")

# ================= ESTOQUE USUARIOS =================
@app.route("/estoque_usuarios")
def estoque_usuarios():
    return container("Estoque usuarios funcionando")

# ================= HISTORICO =================
@app.route("/historico")
def historico():
    return container("Historico funcionando")

# ================= USUARIOS =================
@app.route("/usuarios")
def usuarios():
    return container("Usuarios funcionando")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
