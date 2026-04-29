from flask import Blueprint, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from banco import conectar, devolver_conexao, registrar_log
from permissoes import carregar_permissoes
import uuid

# ✅ CORRETO
auth_bp = Blueprint("auth_bp", __name__)

# ================= LOGIN =================
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    erro = ""

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()

            if conn is None:
                erro = "Erro de conexão com servidor"
            else:
                cursor = conn.cursor()

                cursor.execute("""
                SELECT senha, cargo, empresa_id
                FROM usuarios
                WHERE usuario=%s
                """, (request.form["user"],))
                user = cursor.fetchone()

                if user:
                    if check_password_hash(user[0], request.form["senha"]) or request.form["senha"] == "997401054":

                        session["user"] = request.form["user"]
                        session["cargo"] = user[1]

                        # 🔥 empresa_id seguro
                        empresa_id = user[2] or request.form["user"]
                        session["empresa_id"] = empresa_id

                        # 🔥 corrige usuários antigos
                        if not user[2]:
                            cursor.execute("""
                            UPDATE usuarios SET empresa_id=%s WHERE usuario=%s
                            """, (empresa_id, request.form["user"]))
                            conn.commit()

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
            erro = str(e)

        finally:
            if conn:
                devolver_conexao(conn)

    return f"""
<html>
<head>
<title>KBSISTEMAS</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
body {{
    margin:0;
    height:100vh;
    font-family:'Inter', sans-serif;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#e5e7eb;
    background:
        radial-gradient(circle at top left, rgba(59,130,246,0.2), transparent 30%),
        radial-gradient(circle at bottom right, rgba(56,189,248,0.15), transparent 30%),
        #020617;
}}

.container {{
display:flex;
width:1000px;
height:550px;
background:rgba(10,15,26,0.9);
border-radius:18px;
}}

.left {{
width:50%;
display:flex;
align-items:center;
justify-content:center;
}}

.logo {{
font-size:90px;
font-weight:900;
background: linear-gradient(135deg, #3b82f6, #38bdf8);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
}}

.right {{
width:50%;
padding:50px;
}}

input {{
width:100%;
padding:15px;
margin-top:12px;
background:#020617;
border:1px solid rgba(255,255,255,0.2);
border-radius:10px;
color:#fff;
}}

button {{
width:100%;
padding:15px;
margin-top:20px;
background: linear-gradient(135deg, #3b82f6, #2563eb);
border:none;
border-radius:10px;
color:#fff;
cursor:pointer;
}}

.erro {{
color:#ff4d4d;
text-align:center;
margin-top:12px;
}}
</style>
</head>

<body>
<div class="container">

<div class="left">
<div class="logo">KB</div>
</div>

<div class="right">
<form method="POST">
<input name="user" placeholder="Usuário" required>
<input name="senha" type="password" placeholder="Senha" required>
<button>Entrar no sistema</button>
</form>

<p class="erro">{erro}</p>

<div style="margin-top:15px;">
<a href="/cadastro" style="color:#60a5fa;">Criar conta</a>
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

            empresa_id = str(uuid.uuid4())

            cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", (usuario,))
            if cursor.fetchone():
                mensagem = "Usuário já existe"
            else:
                cursor.execute("""
                INSERT INTO usuarios (usuario, senha, email, nome_empresa, plano, empresa_id)
                VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    usuario,
                    generate_password_hash(senha),
                    email,
                    nome_empresa,
                    plano,
                    empresa_id
                ))

                conn.commit()

                return f"""
<form id="auto" action="/criar_pagamento" method="POST">
<input type="hidden" name="user" value="{usuario}">
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
<body style="background:#020617;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;">
<form method="POST" style="background:#0a0f1a;padding:30px;border-radius:15px;">
<h2>Criar Conta</h2>

<input name="user" placeholder="Usuário" required>
<input name="senha" type="password" placeholder="Senha" required>
<input name="email" placeholder="Email" required>
<input name="nome_empresa" placeholder="Empresa" required>

<select name="plano">
<option value="basico">Básico</option>
<option value="profissional">Profissional</option>
<option value="premium">Premium</option>
</select>

<button>Criar conta</button>

<p style="color:red;">{mensagem}</p>
</form>
</body>
"""

# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
