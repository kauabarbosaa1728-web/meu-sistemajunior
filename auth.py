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
                    erro = "Usuário inativo"
                elif check_password_hash(user[0], request.form["senha"]):
                    session["user"] = request.form["user"]
                    session["cargo"] = user[1]

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                    conn.commit()

                    carregar_permissoes(request.form["user"])
                    registrar_log(request.form["user"], "login", "Login realizado")
                    return redirect("/painel")
                else:
                    erro = "Senha inválida"
            else:
                erro = "Usuário não encontrado"

        except Exception as e:
            erro = f"Erro: {e}"
        finally:
            devolver_conexao(conn)

    return f"""
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" href="/static/logo.png">
    </head>

    <style>
    body {{
        margin:0;
        background:black;
        font-family: monospace;
        color:#00ff00;
    }}

    canvas {{
        position:fixed;
        top:0;
        left:0;
        z-index:0;
    }}

    .box {{
        position:relative;
        z-index:2;
        width:420px;
        margin:auto;
        margin-top:100px;
        padding:30px;
        background:rgba(0,0,0,0.8);
        border:1px solid #00ff00;
        border-radius:10px;
        box-shadow:0 0 20px #00ff00;
    }}

    input, button {{
        width:100%;
        padding:12px;
        margin-top:10px;
        background:black;
        border:1px solid #00ff00;
        color:#00ff00;
    }}

    button:hover {{
        background:#00ff00;
        color:black;
    }}

    .erro {{
        text-align:center;
        color:red;
        margin-top:10px;
    }}

    a {{
        color:#00ff00;
    }}
    </style>

    <canvas id="matrix"></canvas>

    <div class="box">
        <h2 style="text-align:center;">KBSISTEMAS</h2>

        <form method="POST">
            <input name="user" placeholder="Usuário" required>
            <input name="senha" type="password" placeholder="Senha" required>
            <button>ENTRAR</button>
        </form>

        <div class="erro">{erro}</div>

        <div style="text-align:center;margin-top:15px;">
            <a href="/cadastro">Criar conta</a>
        </div>
    </div>

    <script>
    const canvas = document.getElementById("matrix");
    const ctx = canvas.getContext("2d");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const fontSize = 14;
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
    <body style="background:black;color:#00ff00;text-align:center;padding-top:100px;">
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
    </body>
    """


# ================= PAGAMENTO =================
@auth_bp.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():
    return "<h1 style='color:#00ff00;background:black;text-align:center;padding:100px;'>INTEGRAÇÃO COM MERCADO PAGO AQUI</h1>"


# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
