from flask import Flask, render_template_string, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "segredo123"

# 👤 USUÁRIO PRINCIPAL
usuarios = {
    "kaua.barbosa1728@gmail.com": generate_password_hash("997401054")
}

# 🔐 ADMIN
admins = ["kaua.barbosa1728@gmail.com"]

# 📦 ESTOQUE
estoque = {}

# 🔐 LOGIN
html_login = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - KBSistemas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-dark d-flex justify-content-center align-items-center" style="height:100vh;">

<div class="card p-4 shadow" style="width: 350px;">
    <h3 class="text-center mb-3">🔐 KBSistemas</h3>

    <form method="POST">
        <input name="user" class="form-control mb-2" placeholder="Usuário" required>
        <input name="senha" type="password" class="form-control mb-3" placeholder="Senha" required>
        <button class="btn btn-primary w-100">Entrar</button>
    </form>

    <p class="text-danger text-center mt-2">{{erro}}</p>
</div>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def login():
    erro = ""

    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        if user in usuarios and check_password_hash(usuarios[user], senha):
            session["user"] = user
            return redirect("/sistema")
        else:
            erro = "Usuário ou senha inválidos"

    return render_template_string(html_login, erro=erro)

# 📦 SISTEMA (INTERFACE PROFISSIONAL)
@app.route("/sistema", methods=["GET","POST"])
def sistema():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        nome = request.form["produto"]
        qtd = int(request.form["qtd"])
        estoque[nome] = estoque.get(nome, 0) + qtd

    tabela = ""
    for p, q in estoque.items():
        tabela += f"""
        <tr>
            <td>{p}</td>
            <td>{q}</td>
        </tr>
        """

    botao_admin = ""
    if session["user"] in admins:
        botao_admin = '<a href="/criar_usuario" class="btn btn-warning me-2">👤 Criar Usuário</a>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>KBSistemas</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>

    <body class="bg-light">

    <!-- NAVBAR -->
    <nav class="navbar navbar-dark bg-dark px-4">
        <span class="navbar-brand mb-0 h1">📦 KBSistemas</span>
        <div>
            {botao_admin}
            <a href="/logout" class="btn btn-danger ms-2">Sair</a>
        </div>
    </nav>

    <div class="container mt-4">

        <!-- CARDS -->
        <div class="row mb-4">

            <div class="col-md-6">
                <div class="card shadow p-3 text-center">
                    <h5>Total de Produtos</h5>
                    <h2>{len(estoque)}</h2>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card shadow p-3 text-center">
                    <h5>Total em Estoque</h5>
                    <h2>{sum(estoque.values())}</h2>
                </div>
            </div>

        </div>

        <!-- FORM -->
        <div class="card shadow p-4 mb-4">
            <h4>➕ Adicionar Produto</h4>
            <form method="POST" class="row g-3">

                <div class="col-md-6">
                    <input name="produto" class="form-control" placeholder="Nome do produto" required>
                </div>

                <div class="col-md-4">
                    <input name="qtd" type="number" class="form-control" placeholder="Quantidade" required>
                </div>

                <div class="col-md-2">
                    <button class="btn btn-success w-100">Adicionar</button>
                </div>

            </form>
        </div>

        <!-- TABELA -->
        <div class="card shadow p-4">
            <h4>📊 Estoque</h4>

            <table class="table table-striped mt-3">
                <thead class="table-dark">
                    <tr>
                        <th>Produto</th>
                        <th>Quantidade</th>
                    </tr>
                </thead>
                <tbody>
                    {tabela}
                </tbody>
            </table>
        </div>

    </div>

    </body>
    </html>
    """

# 👥 CRIAR USUÁRIO
@app.route("/criar_usuario", methods=["GET", "POST"])
def criar_usuario():
    if "user" not in session or session["user"] not in admins:
        return "Acesso negado"

    if request.method == "POST":
        novo_user = request.form["user"]
        nova_senha = request.form["senha"]

        usuarios[novo_user] = generate_password_hash(nova_senha)
        return "Usuário criado com sucesso!"

    return """
    <h2>Criar Usuário</h2>
    <form method="POST">
        Usuário: <input name="user"><br><br>
        Senha: <input name="senha" type="password"><br><br>
        <button>Criar</button>
    </form>
    """

# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# 🚀 RODAR NO RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
