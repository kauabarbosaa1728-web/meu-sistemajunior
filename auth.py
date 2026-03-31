from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from banco import conectar, devolver_conexao, registrar_log, permissoes_por_plano
from layout import carregar_permissoes

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    erro = ""

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
            SELECT senha, cargo, ativo
            FROM usuarios
            WHERE usuario=%s
            """, (request.form["user"],))
            user = cursor.fetchone()

            if user:
                if not user[2]:
                    erro = "Este usuário está inativo. Fale com o administrador."
                    registrar_log(request.form["user"], "tentativa_login_bloqueada", "Usuário inativo tentou entrar")
                elif check_password_hash(user[0], request.form["senha"]):
                    session["user"] = request.form["user"]
                    session["cargo"] = user[1]

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s", (request.form["user"],))
                    conn.commit()

                    carregar_permissoes(request.form["user"])
                    registrar_log(request.form["user"], "login", "Usuário entrou no sistema")
                    return redirect("/painel")
                else:
                    erro = "Usuário ou senha inválidos"
                    registrar_log(request.form["user"], "tentativa_login_falhou", "Senha inválida")
            else:
                erro = "Usuário ou senha inválidos"
        except Exception as e:
            erro = f"Erro ao fazer login: {e}"
        finally:
            devolver_conexao(conn)

    return f"""
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">
    </head>

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        overflow-y: auto;
        background: #000;
        font-family: 'Share Tech Mono', monospace;
    }}

    #matrix {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        background: #000;
    }}

    .login-wrapper {{
        position: relative;
        z-index: 2;
        width: 100%;
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 30px 20px;
    }}

    .login-box {{
        width: 460px;
        background: rgba(18, 18, 18, 0.88);
        border: 1px solid #2f2f2f;
        border-radius: 18px;
        padding: 35px 30px;
        backdrop-filter: blur(6px);
        color: #e5e7eb;
    }}

    .titulo {{
        text-align: center;
        margin-bottom: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 34px;
        color: #e5e7eb;
        letter-spacing: 3px;
    }}

    .subtitulo {{
        text-align: center;
        margin-bottom: 24px;
        color: #bdbdbd;
        font-size: 14px;
    }}

    .campo {{
        margin-bottom: 16px;
    }}

    .campo label {{
        display: block;
        margin-bottom: 8px;
        color: #d1d5db;
        font-size: 14px;
    }}

    .campo input {{
        width: 100%;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #3a3a3a;
        background: rgba(0,0,0,0.55);
        color: #f3f4f6;
        outline: none;
        font-size: 16px;
        font-family: 'Share Tech Mono', monospace;
    }}

    .campo input:focus {{
        border-color: #777777;
    }}

    .campo input::placeholder {{
        color: #9ca3af;
    }}

    .btn-login {{
        width: 100%;
        padding: 14px;
        border: 1px solid #4a4a4a;
        border-radius: 10px;
        background: #121212;
        color: #e5e7eb;
        font-size: 18px;
        font-family: 'Orbitron', sans-serif;
        cursor: pointer;
        transition: 0.2s;
    }}

    .btn-login:hover {{
        background: #1f1f1f;
        color: white;
    }}

    .erro {{
        margin-top: 16px;
        text-align: center;
        color: #ff6b6b;
        min-height: 20px;
        font-size: 14px;
    }}

    .cadastro-link {{
        margin-top: 18px;
        text-align: center;
    }}

    .cadastro-link a {{
        color: #d1d5db;
        text-decoration: none;
        font-size: 14px;
    }}

    .cadastro-link a:hover {{
        color: #ffffff;
        text-decoration: underline;
    }}

    .planos {{
        margin-top: 28px;
    }}

    .planos h3 {{
        text-align: center;
        margin-bottom: 16px;
        font-size: 18px;
        color: #f3f4f6;
    }}

    .planos-grid {{
        display: grid;
        gap: 12px;
    }}

    .plano {{
        background: linear-gradient(180deg, #141414 0%, #0c0c0c 100%);
        border: 1px solid #2f2f2f;
        border-radius: 12px;
        padding: 14px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}

    .plano strong {{
        display: block;
        color: #ffffff;
        margin-bottom: 6px;
        font-size: 16px;
    }}

    .plano span {{
        color: #c4c4c4;
        font-size: 13px;
        display: block;
        margin-bottom: 6px;
    }}

    .plano .preco {{
        color: #86efac;
        font-size: 18px;
        font-weight: bold;
    }}

    .plano small {{
        color: #8f8f8f;
        font-size: 12px;
    }}
    </style>

    <canvas id="matrix"></canvas>

    <div class="login-wrapper">
        <div class="login-box">
            <div class="titulo">KBSISTEMAS</div>
            <div class="subtitulo">Entre na sua conta ou crie seu cadastro</div>

            <form method="POST">
                <div class="campo">
                    <label>Usuário</label>
                    <input name="user" placeholder="Digite seu usuário" required>
                </div>

                <div class="campo">
                    <label>Senha</label>
                    <input name="senha" type="password" placeholder="Digite sua senha" required>
                </div>

                <button class="btn-login">ENTRAR NA CONTA</button>
            </form>

            <div class="erro">{erro}</div>

            <div class="cadastro-link">
                <a href="/cadastro">Criar cadastro</a>
            </div>

            <div class="planos">
                <h3>Planos mensais</h3>

                <div class="planos-grid">
                    <div class="plano">
                        <strong>Básico</strong>
                        <span>Estoque + Histórico</span>
                        <div class="preco">R$ 39,90/mês</div>
                        <small>Ideal para quem quer começar</small>
                    </div>

                    <div class="plano">
                        <strong>Profissional</strong>
                        <span>Estoque + Transferência + Histórico + Edição</span>
                        <div class="preco">R$ 79,90/mês</div>
                        <small>Mais controle para a operação diária</small>
                    </div>

                    <div class="plano">
                        <strong>Premium</strong>
                        <span>Todos os recursos do operador liberados</span>
                        <div class="preco">R$ 129,90/mês</div>
                        <small>Plano completo para gestão avançada</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
    const canvas = document.getElementById("matrix");
    const ctx = canvas.getContext("2d");

    function resizeCanvas() {{
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }}

    resizeCanvas();

    const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&@";
    const fontSize = 18;
    let columns = Math.floor(canvas.width / fontSize);
    let drops = Array(columns).fill(1);

    function resetDrops() {{
        columns = Math.floor(canvas.width / fontSize);
        drops = Array(columns).fill(1);
    }}

    function drawMatrix() {{
        ctx.fillStyle = "rgba(0, 0, 0, 0.08)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#7a7a7a";
        ctx.font = fontSize + "px monospace";

        for (let i = 0; i < drops.length; i++) {{
            const text = letters[Math.floor(Math.random() * letters.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                drops[i] = 0;
            }}

            drops[i]++;
        }}
    }}

    setInterval(drawMatrix, 38);

    window.addEventListener("resize", () => {{
        resizeCanvas();
        resetDrops();
    }});
    </script>
    """

@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    mensagem = ""
    sucesso = False

    if request.method == "POST":
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            usuario = request.form["user"].strip()
            senha = request.form["senha"].strip()
            email = request.form["email"].strip()
            nome_empresa = request.form["nome_empresa"].strip()
            plano = request.form["plano"].strip().lower()

            if not usuario or not senha or not email or not nome_empresa or not plano:
                mensagem = "Preencha todos os campos."
            else:
                cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", (usuario,))
                existe_usuario = cursor.fetchone()

                cursor.execute("SELECT usuario FROM usuarios WHERE email=%s", (email,))
                existe_email = cursor.fetchone()

                if existe_usuario:
                    mensagem = "Esse usuário já existe."
                elif existe_email:
                    mensagem = "Esse e-mail já está cadastrado."
                else:
                    permissoes = permissoes_por_plano(plano)

                    cursor.execute("""
                    INSERT INTO usuarios (
                        usuario, senha, cargo, online, ativo, email, plano, nome_empresa,
                        pode_estoque, pode_transferencia, pode_historico,
                        pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        usuario,
                        generate_password_hash(senha),
                        "operador",
                        0,
                        1,
                        email,
                        plano,
                        nome_empresa,
                        permissoes["pode_estoque"],
                        permissoes["pode_transferencia"],
                        permissoes["pode_historico"],
                        permissoes["pode_usuarios"],
                        permissoes["pode_editar_estoque"],
                        permissoes["pode_excluir_estoque"],
                        permissoes["pode_logs"]
                    ))

                    conn.commit()
                    registrar_log(usuario, "cadastro", f"Novo cadastro criado | Plano: {plano} | Empresa: {nome_empresa}")
                    mensagem = "Cadastro realizado com sucesso. Agora você já pode entrar na sua conta."
                    sucesso = True

        except Exception as e:
            if conn:
                conn.rollback()
            mensagem = f"Erro ao cadastrar: {e}"
        finally:
            devolver_conexao(conn)

    classe_msg = "sucesso" if sucesso else "erro"

    return f"""
    <head>
        <title>KBSISTEMAS - Cadastro</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">
    </head>

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        background: #000;
        font-family: 'Share Tech Mono', monospace;
        color: #e5e7eb;
        min-height: 100vh;
        padding: 30px 20px;
    }}

    .cadastro-box {{
        width: 100%;
        max-width: 560px;
        margin: 0 auto;
        background: rgba(18, 18, 18, 0.92);
        border: 1px solid #2f2f2f;
        border-radius: 18px;
        padding: 35px 30px;
    }}

    .titulo {{
        text-align: center;
        margin-bottom: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 30px;
        color: #e5e7eb;
        letter-spacing: 2px;
    }}

    .subtitulo {{
        text-align: center;
        margin-bottom: 24px;
        color: #bdbdbd;
        font-size: 14px;
    }}

    .campo {{
        margin-bottom: 16px;
    }}

    .campo label {{
        display: block;
        margin-bottom: 8px;
        color: #d1d5db;
        font-size: 14px;
    }}

    .campo input,
    .campo select {{
        width: 100%;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #3a3a3a;
        background: rgba(0,0,0,0.55);
        color: #f3f4f6;
        outline: none;
        font-size: 15px;
        font-family: 'Share Tech Mono', monospace;
    }}

    .campo input:focus,
    .campo select:focus {{
        border-color: #777777;
    }}

    .btn-cadastrar {{
        width: 100%;
        padding: 14px;
        border: 1px solid #4a4a4a;
        border-radius: 10px;
        background: #121212;
        color: #e5e7eb;
        font-size: 17px;
        font-family: 'Orbitron', sans-serif;
        cursor: pointer;
        transition: 0.2s;
        margin-top: 8px;
    }}

    .btn-cadastrar:hover {{
        background: #1f1f1f;
        color: white;
    }}

    .erro {{
        margin-top: 16px;
        text-align: center;
        color: #ff6b6b;
        font-size: 14px;
    }}

    .sucesso {{
        margin-top: 16px;
        text-align: center;
        color: #86efac;
        font-size: 14px;
    }}

    .voltar {{
        margin-top: 20px;
        text-align: center;
    }}

    .voltar a {{
        color: #d1d5db;
        text-decoration: none;
    }}

    .voltar a:hover {{
        color: #ffffff;
        text-decoration: underline;
    }}

    .planos-box {{
        margin-top: 18px;
        display: grid;
        gap: 10px;
    }}

    .plano {{
        background: linear-gradient(180deg, #141414 0%, #0c0c0c 100%);
        border: 1px solid #2f2f2f;
        border-radius: 12px;
        padding: 12px;
    }}

    .plano strong {{
        display: block;
        color: #ffffff;
        margin-bottom: 4px;
    }}

    .plano .preco {{
        color: #86efac;
        font-weight: bold;
        margin-top: 6px;
    }}

    .plano small {{
        color: #9ca3af;
    }}
    </style>

    <div class="cadastro-box">
        <div class="titulo">CRIAR CADASTRO</div>
        <div class="subtitulo">Preencha os dados para criar sua conta</div>

        <form method="POST">
            <div class="campo">
                <label>Usuário</label>
                <input name="user" placeholder="Escolha seu usuário" required>
            </div>

            <div class="campo">
                <label>Senha</label>
                <input name="senha" type="password" placeholder="Crie sua senha" required>
            </div>

            <div class="campo">
                <label>E-mail</label>
                <input name="email" type="email" placeholder="Seu e-mail" required>
            </div>

            <div class="campo">
                <label>Nome da empresa</label>
                <input name="nome_empresa" placeholder="Nome da sua empresa" required>
            </div>

            <div class="campo">
                <label>Plano</label>
                <select name="plano" required>
                    <option value="basico">Básico - R$ 39,90/mês</option>
                    <option value="profissional">Profissional - R$ 79,90/mês</option>
                    <option value="premium">Premium - R$ 129,90/mês</option>
                </select>
            </div>

            <div class="planos-box">
                <div class="plano">
                    <strong>Básico</strong>
                    Estoque + Histórico
                    <div class="preco">R$ 39,90/mês</div>
                </div>

                <div class="plano">
                    <strong>Profissional</strong>
                    Estoque + Transferência + Histórico + Edição
                    <div class="preco">R$ 79,90/mês</div>
                </div>

                <div class="plano">
                    <strong>Premium</strong>
                    Todos os recursos do operador liberados
                    <div class="preco">R$ 129,90/mês</div>
                </div>
            </div>

            <button class="btn-cadastrar">CRIAR CADASTRO</button>
        </form>

        <div class="{classe_msg}">{mensagem}</div>

        <div class="voltar">
            <a href="/">Voltar para login</a>
        </div>
    </div>
    """

@auth_bp.route("/logout")
def logout():
    usuario = session.get("user")

    if "user" in session:
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET online=0 WHERE usuario=%s", (session["user"],))
            conn.commit()
        except Exception as e:
            print("Erro no logout:", e)
        finally:
            devolver_conexao(conn)

    if usuario:
        registrar_log(usuario, "logout", "Usuário saiu do sistema")

    session.clear()
    return redirect("/")
