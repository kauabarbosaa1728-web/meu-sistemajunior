from flask import Flask
from banco import criar_banco

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
