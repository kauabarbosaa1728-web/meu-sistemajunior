from flask import Flask, session, request, redirect
from datetime import datetime
from werkzeug.security import generate_password_hash

from banco import criar_banco, verificar_pagamento, conectar, devolver_conexao, registrar_log
from layout import acesso_negado

from auth import auth_bp
from dashboard import dashboard_bp
from estoque import estoque_bp
from usuarios import usuarios_bp
from pagamento import pagamento_routes
from logs import logs_bp

# ================= IA =================
from ia_routes import ia_bp

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= BANCO =================
criar_banco()


# ================= LIBERAÇÃO MANUAL =================
def usuario_liberado_manual():
    usuario = session.get("user")
    return usuario in ["kaua", "kaua@gmail.com"]


# ================= VERIFICAR VENCIMENTO =================
def verificar_vencimento(usuario):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT vencimento FROM pagamentos WHERE usuario=%s
        """, (usuario,))

        dado = cursor.fetchone()

        if not dado:
            return False

        vencimento = dado[0]

        if vencimento and datetime.now() > vencimento:
            cursor.execute("""
            UPDATE pagamentos SET status='bloqueado' WHERE usuario=%s
            """, (usuario,))
            conn.commit()
            return False

        return True

    except Exception as e:
        print("Erro vencimento:", e)
        return False

    finally:
        if conn:
            devolver_conexao(conn)


# ================= BLOQUEIO GLOBAL =================
@app.before_request
def bloquear_sistema():
    rotas_livres = ["/", "/login", "/criar_pagamento", "/webhook", "/pagar"]

    if request.path in rotas_livres:
        return

    if "user" not in session:
        return redirect("/")

    usuario = session.get("user")
    cargo = session.get("cargo")

    print("DEBUG USER:", usuario)
    print("DEBUG CARGO:", cargo)
    print("DEBUG PATH:", request.path)

    # 🔥 LIBERA VOCÊ SEMPRE (ANTI BUG)
    if usuario in ["kaua", "kaua@gmail.com"]:
        return

    # 🔥 LIBERA ADMIN
    if cargo == "admin":
        return

    status = verificar_pagamento(usuario)

    print("STATUS REAL:", status)

    if status != "pago":
        return """
        <h1 style='color:red;text-align:center;margin-top:50px;'>
        🚫 Sistema bloqueado<br><br>
        Efetue o pagamento para continuar
        </h1>
        """
    rotas_livres = ["/", "/login", "/criar_pagamento", "/webhook", "/pagar"]

    if "user" not in session:
        return

    if request.path in rotas_livres:
        return

    if session.get("cargo") == "admin":
        return

    if usuario_liberado_manual():
        return

    usuario = session["user"]

    status = verificar_pagamento(usuario)

    print("STATUS REAL:", status)

    if status != "pago":
        return """
        <style>
            body {
                background: #000;
                color: #0f0;
                font-family: 'Courier New', monospace;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                margin:0;
            }

            .box {
                text-align:center;
                background:#111;
                padding:50px;
                border-radius:10px;
                box-shadow: 0 0 20px #0f0;
            }

            h1 { color:red; }

            button {
                margin-top:20px;
                padding:15px 30px;
                background:#0f0;
                border:none;
                font-size:18px;
                cursor:pointer;
                border-radius:5px;
            }

            button:hover {
                background:#00cc00;
            }
        </style>

        <div class="box">
            <h1>🚫 Sistema bloqueado</h1>
            <p>Seu acesso expirou ou está bloqueado</p>

            <a href="/pagar">
                <button>💰 Pagar agora</button>
            </a>
        </div>
        """


# ================= ROTAS =================
app.register_blueprint(usuarios_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(estoque_bp)
app.register_blueprint(pagamento_routes)
app.register_blueprint(logs_bp)
app.register_blueprint(ia_bp)


# ================= ROTAS DIRETAS (ANTI-404) =================
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
    app.run(debug=True)
