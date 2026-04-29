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

    # 🔥 ROTAS LIBERADAS
    rotas_livres = [
        "/",
        "/cadastro",
        "/criar_pagamento",
        "/verificar_pagamento_auto",
        "/webhook",
        "/static"
    ]

    if any(request.path.startswith(r) for r in rotas_livres):
        return

    # 🔥 NÃO LOGADO
    if "user" not in session:
        return redirect("/")

    # 🔥 ADMIN NÃO BLOQUEIA
    if session.get("cargo") == "admin":
        return

    conn = conectar()
    if conn is None:
        return

    cursor = conn.cursor()

    cursor.execute("""
    SELECT vencimento
    FROM pagamentos
    WHERE usuario=%s AND status='pago'
    """, (session["user"],))

    dado = cursor.fetchone()

    # 🔥 SEM PAGAMENTO
    if not dado:
        return """
        <h2 style='text-align:center;margin-top:100px;'>
        ⚠️ Sistema bloqueado<br><br>
        <a href="/pagar">Ir para pagamento</a>
        </h2>
        """

    vencimento = dado[0]

    # 🔥 VENCEU
    if vencimento and vencimento < datetime.now():
        return """
        <h2 style='text-align:center;margin-top:100px;color:red;'>
        ⚠️ Seu plano expirou<br><br>
        <a href="/pagar">Renovar agora</a>
        </h2>
        """

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

# app.register_blueprint(vendas_bp)

# ================= ROTAS DIRETAS =================
@app.route("/usuarios/excluir_usuario/<usuario>", methods=["POST"])
def excluir_usuario_direto(usuario):
    conn = conectar()
    if conn is None:
        return "Erro de conexão"

    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario,))
    cursor.execute("DELETE FROM pagamentos WHERE usuario=%s", (usuario,))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")


@app.route("/usuarios/mudar_plano/<usuario>", methods=["POST"])
def mudar_plano_direto(usuario):
    novo_plano = request.form.get("plano")

    conn = conectar()
    if conn is None:
        return "Erro de conexão"

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios SET plano=%s WHERE usuario=%s
    """, (novo_plano, usuario))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")


@app.route("/usuarios/alterar_senha/<usuario>", methods=["POST"])
def alterar_senha_direto(usuario):
    nova = request.form.get("senha")

    conn = conectar()
    if conn is None:
        return "Erro de conexão"

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios SET senha=%s WHERE usuario=%s
    """, (generate_password_hash(nova), usuario))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")

# ================= START =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
