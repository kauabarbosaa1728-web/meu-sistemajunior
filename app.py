from flask import Flask, session, request, redirect
from datetime import datetime
from werkzeug.security import generate_password_hash
import os
import pytz

from banco import criar_banco, conectar, devolver_conexao
from layout import acesso_negado, container

from auth import auth_bp
from dashboard import dashboard_bp

# 🔥 ESTOQUE
from estoque.routes import estoque_bp

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
from veiculos.rotas import rotas_bp

app = Flask(__name__)
app.secret_key = "segredo123"


# ================= FUNÇÃO DE HORA =================
def agora_sistema():
    fuso = session.get("fuso", "America/Sao_Paulo")
    try:
        tz = pytz.timezone(fuso)
        return datetime.now(tz)
    except:
        return datetime.now()


# ================= BANCO =================
try:
    criar_banco()
except Exception as e:
    print("Erro ao iniciar banco:", e)


# ================= PING =================
@app.route("/ping")
def ping():
    return "ok"


# ================= CONFIGURAÇÕES =================
@app.route("/configuracoes", methods=["GET", "POST"])
def configuracoes():

    if "user" not in session:
        return redirect("/")

    msg = ""

    if request.method == "POST":
        idioma = request.form.get("idioma")
        fuso = request.form.get("fuso")

        session["idioma"] = idioma
        session["fuso"] = fuso

        msg = "✅ Configurações salvas!"

    idioma = session.get("idioma", "pt")
    fuso = session.get("fuso", "America/Sao_Paulo")

    return container(f"""
    <div class="card">
        <h2>⚙️ Configurações</h2>

        <form method="POST">

            <label>🌐 Idioma</label>
            <select name="idioma">
                <option value="pt" {"selected" if idioma == "pt" else ""}>Português</option>
                <option value="en" {"selected" if idioma == "en" else ""}>Inglês</option>
                <option value="es" {"selected" if idioma == "es" else ""}>Espanhol</option>
            </select>

            <label>🕒 Fuso horário</label>
            <select name="fuso">
                <option value="America/Sao_Paulo" {"selected" if fuso == "America/Sao_Paulo" else ""}>Brasil</option>
                <option value="America/New_York" {"selected" if fuso == "America/New_York" else ""}>EUA</option>
                <option value="Europe/Lisbon" {"selected" if fuso == "Europe/Lisbon" else ""}>Portugal</option>
            </select>

            <button>Salvar</button>
        </form>

        <p>{msg}</p>
    </div>
    """)


# ================= NOVAS ROTAS =================
@app.route("/idioma", methods=["GET", "POST"])
def idioma():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        session["idioma"] = request.form.get("idioma")
        return redirect("/configuracoes")

    idioma_atual = session.get("idioma", "pt")

    return container(f"""
    <div class="card">
        <h2>🌍 Idioma</h2>

        <form method="POST">
            <select name="idioma">
                <option value="pt" {"selected" if idioma_atual == "pt" else ""}>Português</option>
                <option value="en" {"selected" if idioma_atual == "en" else ""}>English</option>
                <option value="es" {"selected" if idioma_atual == "es" else ""}>Español</option>
            </select>

            <button>Salvar</button>
        </form>
    </div>
    """)


@app.route("/datahora", methods=["GET", "POST"])
def datahora():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        session["fuso"] = request.form.get("fuso")
        return redirect("/configuracoes")

    fuso = session.get("fuso", "America/Sao_Paulo")

    return container(f"""
    <div class="card">
        <h2>🕒 Data / Hora</h2>

        <form method="POST">
            <select name="fuso">
                <option value="America/Sao_Paulo" {"selected" if fuso == "America/Sao_Paulo" else ""}>Brasil</option>
                <option value="America/New_York" {"selected" if fuso == "America/New_York" else ""}>EUA</option>
                <option value="Europe/Madrid" {"selected" if fuso == "Europe/Madrid" else ""}>Espanha</option>
            </select>

            <button>Salvar</button>
        </form>
    </div>
    """)


# ================= BLOQUEIO GLOBAL SAAS =================
@app.before_request
def bloquear_sistema():

    request.idioma = session.get("idioma", "pt")

    rotas_livres = [
        "/", "/cadastro", "/criar_pagamento",
        "/verificar_pagamento_auto", "/webhook", "/static/"
    ]

    if request.path.startswith("/baixar-pdf"):
        return

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

        if vencimento and vencimento < agora_sistema():
            return """
            <h2 style='text-align:center;margin-top:100px;color:red;'>
            ⚠️ Plano expirado<br><br>
            <a href="/pagar">Renovar agora</a>
            </h2>
            """

        if vencimento:
            dias_restantes = (vencimento - agora_sistema()).days
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

# VEÍCULOS
app.register_blueprint(veiculos_bp)
app.register_blueprint(manutencoes_bp)
app.register_blueprint(dashboard_veiculos_bp)
app.register_blueprint(problemas_bp)
app.register_blueprint(rotas_bp)


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
