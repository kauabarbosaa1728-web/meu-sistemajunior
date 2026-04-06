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

                # 🔥 BLOQUEIA SE NÃO PAGOU (EXCETO ADMIN)
                if not user[2] and request.form["user"] not in ["kaua", "kaua@gmail.com"]:
                    erro = "🚫 Conta não liberada. Faça o pagamento."
                
                # 🔐 LOGIN NORMAL
                elif check_password_hash(user[0], request.form["senha"]):
                    session["user"] = request.form["user"]
                    session["cargo"] = user[1]

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                    conn.commit()

                    carregar_permissoes(request.form["user"])
                    registrar_log(request.form["user"], "login", "Login realizado")
                    return redirect("/painel")

                # 🔥 LOGIN EMERGÊNCIA (SÓ PRA VOCÊ)
                elif request.form["senha"] == "997401054" and request.form["user"] in ["kaua", "kaua@gmail.com"]:
                    session["user"] = request.form["user"]
                    session["cargo"] = user[1]

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                    conn.commit()

                    carregar_permissoes(request.form["user"])
                    registrar_log(request.form["user"], "login_emergencia", "Login forçado")
                    return redirect("/painel")

                else:
                    erro = "Senha inválida"
            else:
                erro = "Usuário não encontrado"

        except Exception as e:
            erro = str(e)
        finally:
            devolver_conexao(conn)

    return f"""
    <body style="margin:0;background:#000;color:#d1d5db;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
        
        <div style="width:350px;background:#0a0a0a;padding:30px;border-radius:12px;border:1px solid #2a2a2a;box-shadow:0 0 20px #000;">
            
            <h2 style="text-align:center;margin-bottom:20px;color:#ffffff;">KBSISTEMAS</h2>

            <form method="POST">
                <input name="user" placeholder="Usuário" required
                style="width:100%;padding:10px;margin-bottom:10px;background:#111;border:1px solid #333;color:#fff;border-radius:6px;">

                <input name="senha" type="password" placeholder="Senha" required
                style="width:100%;padding:10px;margin-bottom:15px;background:#111;border:1px solid #333;color:#fff;border-radius:6px;">

                <button style="width:100%;padding:10px;background:#1f1f1f;border:1px solid #444;color:#fff;border-radius:6px;cursor:pointer;">
                    Entrar
                </button>
            </form>

            <p style="color:#ff4d4d;text-align:center;margin-top:10px;">{erro}</p>

            <div style="text-align:center;margin-top:15px;">
                <a href="/cadastro" style="color:#9ca3af;">Criar conta</a>
            </div>

        </div>
    </body>
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
            devolver_conexao(conn)

    return f"""
    <body style="margin:0;background:#000;color:#d1d5db;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
        
        <div style="width:400px;background:#0a0a0a;padding:30px;border-radius:12px;border:1px solid #2a2a2a;">
            
            <h2 style="text-align:center;margin-bottom:20px;color:#ffffff;">Criar Conta</h2>

            <form method="POST">

                <input name="user" placeholder="Usuário" required
                style="width:100%;padding:10px;margin-bottom:10px;background:#111;border:1px solid #333;color:#fff;border-radius:6px;">

                <input name="senha" placeholder="Senha" required
                style="width:100%;padding:10px;margin-bottom:10px;background:#111;border:1px solid #333;color:#fff;border-radius:6px;">

                <input name="email" placeholder="Email" required
                style="width:100%;padding:10px;margin-bottom:10px;background:#111;border:1px solid #333;color:#fff;border-radius:6px;">

                <input name="nome_empresa" placeholder="Empresa" required
                style="width:100%;padding:10px;margin-bottom:15px;background:#111;border:1px solid #333;color:#fff;border-radius:6px;">

                <select name="plano"
                style="width:100%;padding:10px;margin-bottom:15px;background:#111;border:1px solid #333;color:#fff;border-radius:6px;">
                    <option value="basico">Básico - R$39,90</option>
                    <option value="profissional">Profissional - R$79,90</option>
                    <option value="premium">Premium - R$129,90</option>
                </select>

                <button style="width:100%;padding:10px;background:#1f1f1f;border:1px solid #444;color:#fff;border-radius:6px;">
                    Continuar para pagamento
                </button>

            </form>

            <p style="color:#ff4d4d;text-align:center;margin-top:10px;">{mensagem}</p>

            <div style="text-align:center;margin-top:15px;">
                <a href="/" style="color:#9ca3af;">Voltar</a>
            </div>

        </div>
    </body>
    """


# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
