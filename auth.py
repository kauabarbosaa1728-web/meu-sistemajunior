from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from banco import conectar, devolver_conexao, registrar_log, permissoes_por_plano
from layout import carregar_permissoes
import requests

auth_bp = Blueprint("auth_bp", __name__)

# 🔐 TOKEN MERCADO PAGO
ACCESS_TOKEN = "APP_USR-6569039713831543-033108-32073b03704b3b93eac080da1fe1d0f7-1249023990"

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
            erro = str(e)
        finally:
            devolver_conexao(conn)

    return f"""
    <body style="background:black;color:#00ff00;text-align:center;padding-top:100px;">
        <h1>KBSISTEMAS</h1>

        <form method="POST">
            <input name="user" placeholder="Usuário"><br><br>
            <input name="senha" type="password" placeholder="Senha"><br><br>
            <button>ENTRAR</button>
        </form>

        <p style="color:red;">{erro}</p>

        <a href="/cadastro">Criar conta</a>
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
                <option value="basico">Básico - R$39,90</option>
                <option value="profissional">Profissional - R$79,90</option>
                <option value="premium">Premium - R$129,90</option>
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
    user = request.form["user"]
    senha = request.form["senha"]
    email = request.form["email"]
    empresa = request.form["nome_empresa"]
    plano = request.form["plano"]

    valores = {
        "basico": 39.90,
        "profissional": 79.90,
        "premium": 129.90
    }

    valor = valores.get(plano, 39.90)

    pagamento = {
        "items": [{
            "title": f"Plano {plano}",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": valor
        }],
        "payer": {"email": email},
        "back_urls": {
            "success": f"https://meu-sistemajunior.onrender.com/sucesso?user={user}&senha={senha}&email={email}&empresa={empresa}&plano={plano}"
        },
        "auto_return": "approved"
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        json=pagamento,
        headers=headers
    )

    link = r.json()["init_point"]
    return redirect(link)

# ================= SUCESSO =================
@auth_bp.route("/sucesso")
def sucesso():
    user = request.args.get("user")
    senha = request.args.get("senha")
    email = request.args.get("email")
    empresa = request.args.get("empresa")
    plano = request.args.get("plano")

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        permissoes = permissoes_por_plano(plano)

        cursor.execute("""
        INSERT INTO usuarios (
            usuario, senha, cargo, online, ativo, email, plano, nome_empresa,
            pode_estoque, pode_transferencia, pode_historico,
            pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user, senha, "operador", 0, 1,
            email, plano, empresa,
            permissoes["pode_estoque"],
            permissoes["pode_transferencia"],
            permissoes["pode_historico"],
            permissoes["pode_usuarios"],
            permissoes["pode_editar_estoque"],
            permissoes["pode_excluir_estoque"],
            permissoes["pode_logs"]
        ))

        conn.commit()

        return "<h1 style='color:#0f0;background:black;text-align:center;padding:100px;'>PAGAMENTO APROVADO ✅</h1>"

    finally:
        devolver_conexao(conn)

# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
