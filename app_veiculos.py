from flask import Flask, request, redirect, session
from veiculos import veiculos_bp
from manutencoes import manutencoes_bp
from dashboard import dashboard_bp
from banco import criar_banco, conectar, devolver_conexao
from layout import layout
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "segredo123"

UPLOAD_FOLDER = os.path.join("static", "uploads")

# 🔥 CRIA BANCO
criar_banco()

app.register_blueprint(veiculos_bp)
app.register_blueprint(manutencoes_bp)
app.register_blueprint(dashboard_bp)

# ================= 🔒 PROTEGER =================
@app.before_request
def proteger():
    rotas_livres = ["/login", "/ping"]

    if request.path not in rotas_livres:
        if "user" not in session:
            return redirect("/login")

# ================= 🔐 LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        nome = request.form.get("nome")
        senha = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT nome, senha, cargo,
                   pode_veiculos,
                   pode_manutencoes,
                   pode_dashboard,
                   pode_usuarios,
                   pode_problemas,
                   pode_ver_problemas
            FROM usuarios
            WHERE nome=%s
        """, (nome,))
        user = cursor.fetchone()

        cursor.close()
        devolver_conexao(conn)

        if user:
            (nome_db, senha_db, cargo,
             pode_veiculos,
             pode_manutencoes,
             pode_dashboard,
             pode_usuarios,
             pode_problemas,
             pode_ver_problemas) = user

            if check_password_hash(senha_db, senha):

                if nome_db == "admin":
                    cargo = "admin"

                session["user"] = nome_db
                session["cargo"] = cargo
                session["pode_veiculos"] = pode_veiculos
                session["pode_manutencoes"] = pode_manutencoes
                session["pode_dashboard"] = pode_dashboard
                session["pode_usuarios"] = pode_usuarios
                session["pode_problemas"] = pode_problemas
                session["pode_ver_problemas"] = pode_ver_problemas

                return redirect("/")
            else:
                return layout("<h2>❌ Senha incorreta</h2>")
        else:
            return layout("<h2>❌ Usuário não encontrado</h2>")

    return layout("""
        <h2>🔐 Login</h2>
        <form method="POST">
            <input name="nome" placeholder="Usuário" required><br><br>
            <input name="senha" type="password" placeholder="Senha" required><br><br>
            <button>Entrar</button>
        </form>
    """)

# ================= 🚪 LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= 🔥 PING =================
@app.route("/ping")
def ping():
    return "ok", 200

# ================= 🚨 PROBLEMAS =================
from PIL import Image, ImageDraw

@app.route("/problemas", methods=["GET", "POST"])
def problemas():
    if session.get("pode_problemas") != 1 and session.get("cargo") != "admin":
        return "Acesso negado"

    if request.method == "POST":
        try:
            descricao = request.form.get("descricao")
            foto = request.files.get("foto")
            usuario = session.get("user")

            if not foto:
                return "Nenhuma imagem enviada"

            # 🔥 PERMITE MAIS FORMATOS (CELULAR)
            if not foto.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                return "Envie apenas imagens (jpg, png, webp)"

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            nome_arquivo = secure_filename(f"{datetime.now().timestamp()}_{foto.filename}")
            caminho = os.path.join(UPLOAD_FOLDER, nome_arquivo)

            foto.save(caminho)

            # 🔥 PROCESSA IMAGEM COM SEGURANÇA
            try:
                img = Image.open(caminho).convert("RGB")  # 🔥 força padrão compatível
                draw = ImageDraw.Draw(img)

                texto = f"{usuario} | {datetime.now().strftime('%d/%m/%Y %H:%M')}"

                largura, altura = img.size

                x = 10
                y = altura - 40

                # fundo preto
                draw.rectangle(
                    [(x - 5, y - 5), (x + 400, y + 30)],
                    fill=(0, 0, 0)
                )

                # texto branco
                draw.text((x, y), texto, fill=(255, 255, 255))

                img.save(caminho, "JPEG", quality=90)

            except Exception as e:
                print("Imagem inválida:", e)
                return "Arquivo enviado não é uma imagem válida"

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO problemas (descricao, foto, usuario)
            VALUES (%s, %s, %s)
            """, (descricao, nome_arquivo, usuario))

            conn.commit()
            cursor.close()
            devolver_conexao(conn)

            return redirect("/problemas")

        except Exception as e:
            return f"ERRO: {str(e)}"

    return layout("""
        <h2>🚨 Registrar Problema</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="foto" required><br><br>
            <textarea name="descricao" required></textarea><br><br>
            <button>Enviar</button>
        </form>
    """)
# ================= 📸 VER PROBLEMAS =================
@app.route("/ver_problemas")
def ver_problemas():
    if session.get("pode_ver_problemas") != 1 and session.get("cargo") != "admin":
        return "Acesso negado"

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, descricao, foto, data FROM problemas ORDER BY id DESC")
    dados = cursor.fetchall()

    cursor.close()
    devolver_conexao(conn)

    html = "<h2>📸 Problemas</h2>"

    for id, descricao, foto, data in dados:
        html += "<div style='background:#111;padding:10px;margin:10px;'>"
        html += f"<p>{data}</p>"

        if foto:
            html += f"<img src='/static/uploads/{foto}' width='200'><br>"

        html += f"<p>{descricao}</p>"
        html += f"<a href='/deletar_problema/{id}'>❌ Excluir</a>"
        html += "</div>"

    return layout(html)

# ================= ❌ DELETAR =================
@app.route("/deletar_problema/<int:id>")
def deletar_problema(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM problemas WHERE id=%s", (id,))
    r = cursor.fetchone()

    if r and r[0]:
        caminho = os.path.join(UPLOAD_FOLDER, r[0])
        if os.path.exists(caminho):
            os.remove(caminho)

    cursor.execute("DELETE FROM problemas WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    devolver_conexao(conn)

    return redirect("/ver_problemas")

# ================= 👤 USUÁRIOS =================
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if session.get("user") != "admin":
        return "<h1 style='color:red;text-align:center;'>🚫 Apenas admin</h1>"

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        senha = request.form.get("senha")

        pode_veiculos = 1 if request.form.get("pode_veiculos") else 0
        pode_manutencoes = 1 if request.form.get("pode_manutencoes") else 0
        pode_dashboard = 1 if request.form.get("pode_dashboard") else 0
        pode_usuarios = 1 if request.form.get("pode_usuarios") else 0
        pode_problemas = 1 if request.form.get("pode_problemas") else 0
        pode_ver_problemas = 1 if request.form.get("pode_ver_problemas") else 0

        senha_hash = generate_password_hash(senha)

        cursor.execute("""
            INSERT INTO usuarios 
            (nome, senha, cargo,
             pode_veiculos, pode_manutencoes,
             pode_dashboard, pode_usuarios,
             pode_problemas, pode_ver_problemas)
            VALUES (%s, %s, 'usuario', %s, %s, %s, %s, %s, %s)
        """, (
            nome, senha_hash,
            pode_veiculos,
            pode_manutencoes,
            pode_dashboard,
            pode_usuarios,
            pode_problemas,
            pode_ver_problemas
        ))

        conn.commit()

    cursor.execute("""
        SELECT id, nome, cargo,
               pode_veiculos,
               pode_manutencoes,
               pode_dashboard,
               pode_usuarios,
               pode_problemas,
               pode_ver_problemas
        FROM usuarios
    """)
    dados = cursor.fetchall()

    html = "<h2>👤 Usuários</h2>"

    html += """
    <div class="card">
        <form method="POST">
            <input name="nome" placeholder="Usuário" required>
            <input name="senha" placeholder="Senha" required>

            <label><input type="checkbox" name="pode_veiculos"> Veículos</label><br>
            <label><input type="checkbox" name="pode_manutencoes"> Manutenções</label><br>
            <label><input type="checkbox" name="pode_dashboard"> Dashboard</label><br>
            <label><input type="checkbox" name="pode_usuarios"> Usuários</label><br>
            <label><input type="checkbox" name="pode_problemas"> Problemas</label><br>
            <label><input type="checkbox" name="pode_ver_problemas"> Ver Problemas</label><br><br>

            <button>Criar Usuário</button>
        </form>
    </div>
    """

    html += "<div class='card'><h3>Lista</h3>"

    for u in dados:
        html += f"""
        <div style="margin-bottom:15px;">
            <p>
            👤 {u[1]} ({u[2]})<br>
            🚗 {u[3]} | 🔧 {u[4]} | 📊 {u[5]} | 👤 {u[6]} | ⚠️ {u[7]} | 📋 {u[8]}
            </p>

            <form method="POST" action="/trocar_senha_admin/{u[0]}">
                <input name="nova" placeholder="Nova senha">
                <button>🔐 Trocar Senha</button>
            </form>

            <a href="/excluir_usuario/{u[0]}" onclick="return confirm('Tem certeza?')">
               ❌ Excluir
            </a>
        </div>
        """

    html += "</div>"

    cursor.close()
    devolver_conexao(conn)

    return layout(html)

# ================= EXCLUIR =================
@app.route("/excluir_usuario/<int:id>")
def excluir_usuario(id):
    if session.get("user") != "admin":
        return "Acesso negado"

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    devolver_conexao(conn)

    return redirect("/usuarios")

# ================= TROCAR SENHA =================
@app.route("/trocar_senha_admin/<int:id>", methods=["POST"])
def trocar_senha_admin(id):
    if session.get("user") != "admin":
        return "Acesso negado"

    nova = request.form.get("nova")

    if not nova:
        return redirect("/usuarios")

    conn = conectar()
    cursor = conn.cursor()

    senha_hash = generate_password_hash(nova)
    cursor.execute("UPDATE usuarios SET senha=%s WHERE id=%s", (senha_hash, id))
    conn.commit()

    cursor.close()
    devolver_conexao(conn)

    return redirect("/usuarios")

# ================= HOME =================
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return layout("""
        <a href="/logout">Sair</a>
        <h2>🚗 Sistema</h2>

        <div class="grid-botoes">
            <a href="/veiculos">🚗 Veículos</a>
            <a href="/manutencoes">🔧 Manutenções</a>
            <a href="/dashboard">📊 Dashboard</a>
            <a href="/usuarios">👤 Usuários</a>
            <a href="/problemas">⚠️ Problemas</a>
            <a href="/ver_problemas">📋 Ver Problemas</a>
        </div>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
