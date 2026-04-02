from flask import Flask, session, request, redirect
from banco import criar_banco, verificar_pagamento

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
    rotas_livres = ["/", "/login", "/criar_pagamento", "/webhook"]

    if "user" not in session:
        return

    if any(r in request.path for r in rotas_livres):
        return

    status = verificar_pagamento(session["user"])

    if status == "bloqueado":
        return """
        <h1 style='color:red;text-align:center;margin-top:50px;'>
        🚫 Sistema bloqueado<br><br>
        Efetue o pagamento para continuar
        </h1>
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
