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
        user = request.form.get("user")
        senha = request.form.get("senha")

        conn = conectar()
        if not conn:
            return "Erro banco"

        cursor = conn.cursor()
        cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s",(user,))
        dado = cursor.fetchone()
        conn.close()

        if dado and check_password_hash(dado[0], senha):
            session["user"] = user
            session["cargo"] = dado[1]
            return redirect("/dashboard")

        erro = "Login inválido"

    return f"""<form method="POST">
    <input name="user"><input type="password" name="senha">
    <button>LOGIN</button><p>{erro}</p></form>"""

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

    try:
        conn = conectar()
        cursor = conn.cursor()

        if request.method == "POST":
            produto = request.form.get("produto")
            qtd = request.form.get("qtd")
            categoria = request.form.get("categoria")

            if produto and qtd:
                try:
                    qtd = int(qtd)
                except:
                    return container("<h3>Quantidade inválida</h3>")

                cursor.execute("""
                INSERT INTO estoque (produto, quantidade, categoria)
                VALUES (%s,%s,%s)
                """,(produto,qtd,categoria))

                conn.commit()

        cursor.execute("SELECT * FROM estoque")
        dados = cursor.fetchall()
        conn.close()

        tabela=""
        for d in dados:
            tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td></tr>"

        return container(f"""
        <h2>Produtos</h2>
        <form method="POST">
            <input name="produto" placeholder="Produto">
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

    except Exception as e:
        print("ERRO ESTOQUE:", e)
        return container("<h3>Erro interno</h3>")

# ================= TRANSFERENCIA =================
@app.route("/transferencia", methods=["GET","POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    try:
        conn = conectar()
        cursor = conn.cursor()

        if request.method == "POST":
            produto = request.form.get("produto")
            qtd = request.form.get("qtd")

            if produto and qtd:
                try:
                    qtd = int(qtd)
                except:
                    return container("<h3>Quantidade inválida</h3>")

                cursor.execute("""
                INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
                VALUES (%s,%s,%s,%s,%s)
                """,(produto,qtd,
                     request.form.get("origem"),
                     request.form.get("destino"),
                     session["user"]))

                conn.commit()

        cursor.execute("SELECT * FROM transferencias")
        dados = cursor.fetchall()
        conn.close()

        tabela=""
        for d in dados:
            tabela += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td><td>{d[5]}</td></tr>"

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

    except Exception as e:
        print("ERRO TRANSF:", e)
        return container("<h3>Erro interno</h3>")

# ================= ROTAS QUE FALTAVAM =================
@app.route("/correcao")
def correcao():
    return container("<h2>Correções funcionando</h2>")

@app.route("/estoque_usuarios")
def estoque_usuarios():
    return container("<h2>Estoque usuários funcionando</h2>")

@app.route("/historico")
def historico():
    return container("<h2>Histórico funcionando</h2>")

@app.route("/usuarios")
def usuarios():
    return container("<h2>Usuários funcionando</h2>")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
