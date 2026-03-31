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

    * {{ box-sizing: border-box; }}

    body {{
        margin: 0;
        background: #000;
        font-family: 'Share Tech Mono', monospace;
    }}

    #matrix {{
        position: fixed;
        width: 100%;
        height: 100%;
        z-index: 0;
    }}

    .login-wrapper {{
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }}

    .login-box {{
        width: 460px;
        background: rgba(18,18,18,0.9);
        padding: 35px;
        border-radius: 18px;
        border: 1px solid #2f2f2f;
        color: #e5e7eb;
    }}

    .titulo {{
        text-align: center;
        font-size: 34px;
        font-family: 'Orbitron';
        letter-spacing: 3px;
    }}

    .subtitulo {{
        text-align: center;
        margin-bottom: 20px;
        color: #aaa;
    }}

    .campo input {{
        width: 100%;
        padding: 12px;
        margin-top: 10px;
        background: #000;
        border: 1px solid #333;
        color: white;
    }}

    .btn-login {{
        width: 100%;
        padding: 12px;
        margin-top: 15px;
        background: #111;
        border: 1px solid #444;
        color: white;
        cursor: pointer;
    }}

    .erro {{
        color: red;
        text-align: center;
        margin-top: 10px;
    }}

    .planos {{
        margin-top: 25px;
    }}

    .plano {{
        border: 1px solid #333;
        padding: 10px;
        margin-top: 10px;
        border-radius: 10px;
    }}

    .preco {{
        color: #00ff88;
        font-weight: bold;
    }}
    </style>

    <canvas id="matrix"></canvas>

    <div class="login-wrapper">
        <div class="login-box">

            <div class="titulo">KBSISTEMAS</div>
            <div class="subtitulo">Entre na sua conta ou crie seu cadastro</div>

            <form method="POST">
                <div class="campo">
                    <input name="user" placeholder="Usuário" required>
                </div>

                <div class="campo">
                    <input name="senha" type="password" placeholder="Senha" required>
                </div>

                <button class="btn-login">ENTRAR NA CONTA</button>
            </form>

            <div class="erro">{erro}</div>

            <div style="text-align:center;margin-top:15px;">
                <a href="/cadastro" style="color:#ccc;">Criar cadastro</a>
            </div>

            <div class="planos">
                <h3>Planos mensais</h3>

                <div class="plano">
                    <strong>Básico</strong><br>
                    Estoque + Histórico<br>
                    <span class="preco">R$ 39,90/mês</span>
                </div>

                <div class="plano">
                    <strong>Profissional</strong><br>
                    Estoque + Transferência + Histórico<br>
                    <span class="preco">R$ 79,90/mês</span>
                </div>
            </div>

        </div>
    </div>

    <script>
    const canvas = document.getElementById("matrix");
    const ctx = canvas.getContext("2d");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const fontSize = 16;
    const columns = canvas.width / fontSize;
    const drops = Array(Math.floor(columns)).fill(1);

    function draw() {{
        ctx.fillStyle = "rgba(0,0,0,0.05)";
        ctx.fillRect(0,0,canvas.width,canvas.height);

        ctx.fillStyle = "#0f0";
        ctx.font = fontSize + "px monospace";

        for(let i=0;i<drops.length;i++) {{
            const text = letters[Math.floor(Math.random()*letters.length)];
            ctx.fillText(text,i*fontSize,drops[i]*fontSize);

            if(drops[i]*fontSize > canvas.height) drops[i]=0;
            drops[i]++;
        }}
    }}

    setInterval(draw, 33);
    </script>
    """


# ================= CADASTRO =================
@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    mensagem = ""

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            usuario = request.form["user"]
            senha = request.form["senha"]
            email = request.form["email"]
            nome_empresa = request.form["nome_empresa"]
            plano = request.form["plano"]

            cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", (usuario,))
            if cursor.fetchone():
                mensagem = "Usuário já existe"
            else:
                return f"""
<form id="auto" action="/criar_pagamento" method="POST">
<input type="hidden" name="user" value="{usuario}">
<input type="hidden" name="senha" value="{generate_password_hash(senha)}">
<input type="hidden" name="email" value="{email}">
<input type="hidden" name="nome_empresa" value="{nome_empresa}">
<input type="hidden" name="plano" value="{plano}">
</form>
<script>document.getElementById("auto").submit();</script>
"""
        except Exception as e:
            mensagem = str(e)
        finally:
            devolver_conexao(conn)

    return f"""
    <div style="background:#000;color:white;text-align:center;padding-top:100px;">
        <h1>Cadastro</h1>

        <form method="POST">
            <input name="user" placeholder="Usuário"><br><br>
            <input name="senha" placeholder="Senha"><br><br>
            <input name="email" placeholder="Email"><br><br>
            <input name="nome_empresa" placeholder="Empresa"><br><br>

            <select name="plano">
                <option value="basico">Básico</option>
                <option value="profissional">Profissional</option>
                <option value="premium">Premium</option>
            </select><br><br>

            <button>Cadastrar</button>
        </form>

        <p style="color:red;">{mensagem}</p>

        <a href="/">Voltar</a>
    </div>
    """


# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
