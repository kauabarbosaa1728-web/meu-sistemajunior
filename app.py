from flask import Flask, session, request, redirect
from datetime import datetime
from werkzeug.security import generate_password_hash
import os

from banco import criar_banco, verificar_pagamento, conectar, devolver_conexao
from layout import acesso_negado

from auth import auth_bp
from dashboard import dashboard_bp
from estoque import estoque_bp
from usuarios import usuarios_bp
from pagamento import pagamento_routes
from logs import logs_bp
from ia_routes import ia_bp

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= BANCO =================
try:
    criar_banco()
except Exception as e:
    print("Erro ao iniciar banco:", e)


# ================= BLOQUEIO GLOBAL =================
@app.before_request
def bloquear_sistema():
    try:
        rotas_livres = ["/", "/login", "/cadastro", "/criar_pagamento", "/webhook", "/pagar"]

        if request.path in rotas_livres:
            return

        if "user" not in session:
            return redirect("/")

        usuario = session.get("user")
        cargo = session.get("cargo")

        # 🔥 ADMIN LIBERADO
        if cargo == "admin":
            return

        # 🔒 VERIFICA PAGAMENTO
        status = verificar_pagamento(usuario)

        print("STATUS DEBUG:", status)

        if str(status).strip().lower() != "pago":
            return """
            <h1 style='color:red;text-align:center;margin-top:50px;'>
            🚫 Sistema bloqueado<br><br>
            Efetue o pagamento para continuar
            </h1>
            """
    except Exception as e:
        print("Erro no bloqueio:", e)


# ================= ROTAS =================
app.register_blueprint(usuarios_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(estoque_bp)
app.register_blueprint(pagamento_routes)
app.register_blueprint(logs_bp)
app.register_blueprint(ia_bp)


# ================= ROTAS DIRETAS =================
@app.route("/usuarios/excluir_usuario/<usuario>", methods=["POST"])
def excluir_usuario_direto(usuario):
    conn = conectar()
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

# ================= BLOQUEIO GLOBAL (DESATIVADO TOTAL) =================
@app.before_request
def bloquear_sistema():
    return
