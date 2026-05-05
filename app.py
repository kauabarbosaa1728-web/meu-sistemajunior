from flask import Flask, session, request, redirect
from datetime import datetime
from werkzeug.security import generate_password_hash
import os

from banco import criar_banco, conectar, devolver_conexao
from layout import acesso_negado

from auth import auth_bp
from dashboard import dashboard_bp
from estoque import estoque_bp
from usuarios import usuarios_bp
from pagamento import pagamento_routes
from logs import logs_bp
from ia_routes import ia_bp
from financeiro import financeiro_bp
from vendas import vendas_bp
from relatorios import relatorios_bp

# 🔥 VEÍCULOS
from veiculos.veiculos import veiculos_bp
from veiculos.manutencoes import manutencoes_bp
from veiculos.dashboard_veiculos import dashboard_veiculos_bp
from veiculos.problemas import problemas_bp

# 🔥 NOVO: ROTAS (GPS)
from veiculos.rotas import rotas_bp

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= BANCO =================
try:
    criar_banco()
except Exception as e:
    print("Erro ao iniciar banco:", e)

# ================= PING =================
@app.route("/ping")
def ping():
    return "ok"

# ================= BLOQUEIO GLOBAL SAAS =================
@app.before_request
def bloquear_sistema():

    rotas_livres = [
        "/", "/cadastro", "/criar_pagamento",
        "/verificar_pagamento_auto", "/webhook", "/static/"
    ]

    if any(request.path.startswith(r) for r in rotas_livres):
        return

    if "user" not in session:
        return redirect("/")

    if session.get("cargo") == "admin":
        return

    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT status, vencimento
        FROM pagamentos
        WHERE usuario=%s
        """, (session["user"],))

        dado = cursor.fetchone()

        if not dado:
            return """
            <h2 style='text-align:center;margin-top:100px;'>
            ⚠️ Nenhum plano ativo<br><br>
            <a href="/pagar">Assinar agora</a>
            </h2>
            """

        status, vencimento = dado

        if status != "pago":
            return """
            <h2 style='text-align:center;margin-top:100px;'>
            ⚠️ Pagamento pendente<br><br>
            <a href="/pagar">Pagar agora</a>
            </h2>
            """

        if vencimento and vencimento < datetime.now():
            return """
            <h2 style='text-align:center;margin-top:100px;color:red;'>
            ⚠️ Plano expirado<br><br>
            <a href="/pagar">Renovar agora</a>
            </h2>
            """

        if vencimento:
            dias_restantes = (vencimento - datetime.now()).days
            if dias_restantes <= 3:
                request.aviso_plano = f"⚠️ Seu plano vence em {dias_restantes} dia(s)"

    except Exception as e:
        print("Erro no bloqueio:", e)

    finally:
        devolver_conexao(conn)

# ================= BLUEPRINTS =================
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(estoque_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(pagamento_routes)
app.register_blueprint(logs_bp)
app.register_blueprint(ia_bp)
app.register_blueprint(financeiro_bp)
app.register_blueprint(relatorios_bp)

# 🔥 VEÍCULOS
app.register_blueprint(veiculos_bp)
app.register_blueprint(manutencoes_bp)
app.register_blueprint(dashboard_veiculos_bp)
app.register_blueprint(problemas_bp)

# 🔥 NOVO: GPS / ROTAS
app.register_blueprint(rotas_bp)

# app.register_blueprint(vendas_bp)

# ================= ROTAS DIRETAS =================
@app.route("/usuarios/excluir_usuario/<usuario>", methods=["POST"])
def excluir_usuario_direto(usuario):
    conn = conectar()
    if conn is None:
        return "Erro de conexão"

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario,))
        cursor.execute("DELETE FROM pagamentos WHERE usuario=%s", (usuario,))
        conn.commit()
    finally:
        devolver_conexao(conn)

    return redirect("/usuarios")


@app.route("/usuarios/mudar_plano/<usuario>", methods=["POST"])
def mudar_plano_direto(usuario):
    novo_plano = request.form.get("plano")

    conn = conectar()
    if conn is None:
        return "Erro de conexão"

    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE usuarios SET plano=%s WHERE usuario=%s
        """, (novo_plano, usuario))
        conn.commit()
    finally:
        devolver_conexao(conn)

    return redirect("/usuarios")


@app.route("/usuarios/alterar_senha/<usuario>", methods=["POST"])
def alterar_senha_direto(usuario):
    nova = request.form.get("senha")

    conn = conectar()
    if conn is None:
        return "Erro de conexão"

    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE usuarios SET senha=%s WHERE usuario=%s
        """, (generate_password_hash(nova), usuario))
        conn.commit()
    finally:
        devolver_conexao(conn)

    return redirect("/usuarios")

# ================= START =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
