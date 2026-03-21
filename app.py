from flask import Flask, render_template_string, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "segredo123"

# 👤 USUÁRIO PRINCIPAL (SEU LOGIN)
usuarios = {
    "kaua.barbosa1728@gmail.com": generate_password_hash("997401054")
}

# 🔐 ADMIN (SÓ VOCÊ)
admins = ["kaua.barbosa1728@gmail.com"]

# 📦 Estoque
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

# 📦 SISTEMA
@app.route("/sistema", methods=["GET","POST"])
def sistema():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        nome = request.form["produto"]
        qtd = int(request.form["qtd"])
        estoque[nome] = estoque.get(nome, 0) + qtd

    itens_html = ""
    for p, q in estoque.items():
        itens_html += f"<li class='list-group-item'>{p}: {q}</li>"

    botao_admin = ""
    if session["user"] in admins:
        botao_admin = '<a href="/criar_usuario" class="btn btn-warning me-2">Criar Usuário</a>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Estoque</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>

    <body class="bg-light">

    <div class="container mt-5">

        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>📦 KBSistemas - Estoque</h2>
            <div>
                {botao_admin}
                <a href="/logout" class="btn btn-danger">Sair</a>
            </div>
        </div>

        <div class="card p-4 mb-4 shadow">
            <form method="POST" class="row g-3">
                <div class="col-md-6">
                    <input name="produto" class="form-control" placeholder="Produto" required>
                </div>

                <div class="col-md-4">
                    <input name="qtd" type="number" class="form-control" placeholder="Quantidade" required>
                </div>

                <div class="col-md-2">
                    <button class="btn btn-success w-100">Adicionar</button>
                </div>
            </form>
        </div>

        <div class="card p-3 shadow">
            <h4>📊 Estoque Atual</h4>
            <ul class="list-group">
                {itens_html}
            </ul>
        </div>

    </div>

    </body>
    </html>
    """

# 👥 CRIAR USUÁRIO (SÓ ADMIN)
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
