from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from banco import conectar, devolver_conexao, registrar_log, permissoes_por_plano
from layout import carregar_permissoes

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    erro = ""

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
            SELECT senha, cargo, ativo
            FROM usuarios
            WHERE usuario=%s
            """, (request.form["user"],))
            user = cursor.fetchone()

            if user:
                if not user[2]:
                    erro = "Este usuário está inativo. Fale com o administrador."
                    registrar_log(request.form["user"], "tentativa_login_bloqueada", "Usuário inativo tentou entrar")
                elif check_password_hash(user[0], request.form["senha"]):
                    session["user"] = request.form["user"]
                    session["cargo"] = user[1]

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                    conn.commit()

                    carregar_permissoes(request.form["user"])
                    registrar_log(request.form["user"], "login", "Usuário entrou no sistema")
                    return redirect("/painel")
                else:
                    erro = "Usuário ou senha inválidos"
                    registrar_log(request.form["user"], "tentativa_login_falhou", "Senha inválida")
            else:
                erro = "Usuário ou senha inválidos"
        except Exception as e:
            erro = f"Erro ao fazer login: {e}"
        finally:
            devolver_conexao(conn)

    return f"""
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">
    </head>

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        overflow-y: auto;
        background: #000;
        font-family: 'Share Tech Mono', monospace;
    }}

    #matrix {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        background: #000;
    }}

    .login-wrapper {{
        position: relative;
        z-index: 2;
        width: 100%;
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 30px 20px;
    }}

    .login-box {{
        width: 460px;
        background: rgba(18, 18, 18, 0.88);
        border: 1px solid #2f2f2f;
        border-radius: 18px;
        padding: 35px 30px;
        backdrop-filter: blur(6px);
        color: #e5e7eb;
    }}

    .titulo {{
        text-align: center;
        margin-bottom: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 34px;
        color: #e5e7eb;
        letter-spacing: 3px;
    }}

    .subtitulo {{
        text-align: center;
        margin-bottom: 24px;
        color: #bdbdbd;
        font-size: 14px;
    }}

    .campo {{
        margin-bottom: 16px;
    }}

    .campo label {{
        display: block;
        margin-bottom: 8px;
        color: #d1d5db;
        font-size: 14px;
    }}

    .campo input {{
        width: 100%;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #3a3a3a;
        background: rgba(0,0,0,0.55);
        color: #f3f4f6;
        outline: none;
        font-size: 16px;
        font-family: 'Share Tech Mono', monospace;
    }}

    .campo input:focus {{
        border-color: #777777;
    }}

    .campo input::placeholder {{
        color: #9ca3af;
    }}

    .btn-login {{
        width: 100%;
        padding: 14px;
        border: 1px solid #4a4a4a;
        border-radius: 10px;
        background: #121212;
        color: #e5e7eb;
        font-size: 18px;
        font-family: 'Orbitron', sans-serif;
        cursor: pointer;
        transition: 0.2s;
    }}

    .btn-login:hover {{
        background: #1f1f1f;
        color: white;
    }}

    .erro {{
        margin-top: 16px;
        text-align: center;
        color: #ff6b6b;
        min-height: 20px;
        font-size: 14px;
    }}

    .cadastro-link {{
        margin-top: 18px;
        text-align: center;
    }}

    .cadastro-link a {{
        color: #d1d5db;
        text-decoration: none;
        font-size: 14px;
    }}

    .cadastro-link a:hover {{
        color: #ffffff;
        text-decoration: underline;
    }}

    .planos {{
        margin-top: 28px;
    }}

    .planos h3 {{
        text-align: center;
        margin-bottom: 16px;
        font-size: 18px;
        color: #f3f4f6;
    }}
@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    mensagem = ""
    sucesso = False

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()
           from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from banco import conectar, devolver_conexao, registrar_log, permissoes_por_plano
from layout import carregar_permissoes

auth_bp = Blueprint("auth_bp", __name__)

# ================= LOGIN =================
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    erro = ""

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
            SELECT senha, cargo, ativo
            FROM usuarios
            WHERE usuario=%s
            """, (request.form["user"],))
            user = cursor.fetchone()

            if user:
                if not user[2]:
                    erro = "Este usuário está inativo."
                elif check_password_hash(user[0], request.form["senha"]):
                    session["user"] = request.form["user"]
                    session["cargo"] = user[1]

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                    conn.commit()

                    carregar_permissoes(request.form["user"])
                    registrar_log(request.form["user"], "login", "Usuário entrou no sistema")
                    return redirect("/painel")
                else:
                    erro = "Usuário ou senha inválidos"
            else:
                erro = "Usuário ou senha inválidos"

        except Exception as e:
            erro = f"Erro ao fazer login: {e}"
        finally:
            devolver_conexao(conn)

    return f"""
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" href="/static/logo.png">
    </head>

    <style>
    body {{
        margin: 0;
        background: #000;
        font-family: monospace;
        color: white;
    }}

    .login-box {{
        width: 460px;
        margin: auto;
        margin-top: 100px;
        background: #111;
        padding: 30px;
        border-radius: 12px;
    }}

    input, button {{
        width: 100%;
        padding: 10px;
        margin-top: 10px;
    }}

    .erro {{
        color: red;
        text-align: center;
    }}
    </style>

    <div class="login-box">
        <h2>KBSISTEMAS</h2>

        <form method="POST">
            <input name="user" placeholder="Usuário" required>
            <input name="senha" type="password" placeholder="Senha" required>
            <button>Entrar</button>
        </form>

        <div class="erro">{erro}</div>

        <div style="text-align:center;">
            <a href="/cadastro">Criar conta</a>
        </div>
    </div>
    """


# ================= CADASTRO =================
@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    mensagem = ""
    sucesso = False

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            usuario = request.form["user"].strip()
            senha = request.form["senha"].strip()
            email = request.form["email"].strip()
            nome_empresa = request.form["nome_empresa"].strip()
            plano = request.form["plano"].strip().lower()

            if not usuario or not senha or not email or not nome_empresa or not plano:
                mensagem = "Preencha todos os campos."
            else:
                cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", (usuario,))
                existe_usuario = cursor.fetchone()

                cursor.execute("SELECT usuario FROM usuarios WHERE email=%s", (email,))
                existe_email = cursor.fetchone()

                if existe_usuario:
                    mensagem = "Esse usuário já existe."
                elif existe_email:
                    mensagem = "Esse e-mail já está cadastrado."
                else:
                    return f"""
                    <form id="auto" action="/criar_pagamento" method="POST">
                        <input type="hidden" name="user" value="{usuario}">
                        <input type="hidden" name="senha" value="{generate_password_hash(senha)}">
                        <input type="hidden" name="email" value="{email}">
                        <input type="hidden" name="nome_empresa" value="{nome_empresa}">
                        <input type="hidden" name="plano" value="{plano}">
                    </form>

                    <script>
                        document.getElementById("auto").submit();
                    </script>
                    """

        except Exception as e:
            if conn:
                conn.rollback()
            mensagem = f"Erro ao cadastrar: {e}"
        finally:
            devolver_conexao(conn)

    classe_msg = "sucesso" if sucesso else "erro"

    return f"""
    <div style="width:460px;margin:auto;margin-top:100px;background:#111;padding:30px;border-radius:12px;">
        <h2>CRIAR CADASTRO</h2>

        <form method="POST">
            <input name="user" placeholder="Usuário" required>
            <input name="senha" type="password" placeholder="Senha" required>
            <input name="email" placeholder="Email" required>
            <input name="nome_empresa" placeholder="Empresa" required>

            <select name="plano">
                <option value="basico">Básico</option>
                <option value="profissional">Profissional</option>
                <option value="premium">Premium</option>
            </select>

            <button>Cadastrar</button>
        </form>

        <p style="color:red;text-align:center;">{mensagem}</p>

        <div style="text-align:center;">
            <a href="/">Voltar</a>
        </div>
    </div>
    """


# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
