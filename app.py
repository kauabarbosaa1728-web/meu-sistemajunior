from flask import Flask, session, request, redirect
from banco import criar_banco, verificar_pagamento, conectar

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

# Criar banco automaticamente
criar_banco()

# ================= BLOQUEIO GLOBAL =================
@app.before_request
def bloquear_sistema():
    rotas_livres = ["/", "/login", "/criar_pagamento", "/webhook", "/pagar"]

    if "user" not in session:
        return

    if any(r in request.path for r in rotas_livres):
        return

    # 🔥 VERIFICA SE É ADMIN
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT cargo FROM usuarios WHERE usuario=%s", (session["user"],))
        user = cursor.fetchone()

        if user and user[0] == "admin":
            return  # 👈 ADMIN NUNCA BLOQUEIA

    except:
        pass
    finally:
        try:
            conn.close()
        except:
            pass

    # 🔒 BLOQUEIO NORMAL
    status = verificar_pagamento(session["user"])

    if status == "bloqueado":
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

            h1 {
                color:red;
            }

            p {
                margin-top:10px;
            }

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
            <p>Efetue o pagamento para continuar</p>

            <a href="/pagar">
                <button>💰 Pagar agora</button>
            </a>
        </div>
        """

# ================= ROTAS =================
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(estoque_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(pagamento_routes)
app.register_blueprint(logs_bp)

# ================= IA =================
app.register_blueprint(ia_bp)

# ================= START =================
if __name__ == "__main__":
    app.run(debug=True)
