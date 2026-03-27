from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

app = Flask(__name__)
app.secret_key = "segredo123"

# ================= CONEXÃO =================
def conectar():
    return psycopg2.connect(
        host="ep-calm-moon-acucwei3-pooler.sa-east-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_zGebRqQWoB06",
        port="5432",
        sslmode="require"
    )

# ================= LOGS =================
def registrar_log(usuario, acao, detalhes=""):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO logs (usuario, acao, detalhes)
        VALUES (%s, %s, %s)
        """, (usuario, acao, detalhes))
        conn.commit()
    except Exception as e:
        print("Erro ao registrar log:", e)
    finally:
        if conn:
            conn.close()

# ================= FUNÇÕES DE PERMISSÃO =================
def acesso_negado():
    return container("""
    <div class="card">
        <h2 class="erro">⛔ Você não tem autorização para acessar esta área.</h2>
        <p>Fale com um administrador para liberar esta permissão.</p>
        <p><a href="/painel">⬅ Voltar para o painel</a></p>
    </div>
    """)

def carregar_permissoes(usuario):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT cargo,
               pode_estoque,
               pode_transferencia,
               pode_historico,
               pode_usuarios,
               pode_editar_estoque,
               pode_excluir_estoque,
               pode_logs,
               ativo
        FROM usuarios
        WHERE usuario=%s
        """, (usuario,))
        dado = cursor.fetchone()

        if dado:
            session["cargo"] = dado[0]
            session["pode_estoque"] = bool(dado[1])
            session["pode_transferencia"] = bool(dado[2])
            session["pode_historico"] = bool(dado[3])
            session["pode_usuarios"] = bool(dado[4])
            session["pode_editar_estoque"] = bool(dado[5])
            session["pode_excluir_estoque"] = bool(dado[6])
            session["pode_logs"] = bool(dado[7])
            session["ativo"] = bool(dado[8])
    finally:
        if conn:
            conn.close()

def tem_permissao(nome):
    if session.get("cargo") == "admin":
        return True
    return bool(session.get(nome, False))

# ================= BANCO =================
def criar_banco():
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            senha TEXT,
            cargo TEXT,
            online INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            pode_estoque INTEGER DEFAULT 0,
            pode_transferencia INTEGER DEFAULT 0,
            pode_historico INTEGER DEFAULT 0,
            pode_usuarios INTEGER DEFAULT 0,
            pode_editar_estoque INTEGER DEFAULT 0,
            pode_excluir_estoque INTEGER DEFAULT 0,
            pode_logs INTEGER DEFAULT 0
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id SERIAL PRIMARY KEY,
            produto TEXT,
            quantidade INTEGER,
            categoria TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transferencias (
            id SERIAL PRIMARY KEY,
            produto TEXT,
            quantidade INTEGER,
            origem TEXT,
            destino TEXT,
            usuario TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            usuario TEXT,
            acao TEXT,
            detalhes TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        colunas_usuarios = [
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ativo INTEGER DEFAULT 1",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pode_estoque INTEGER DEFAULT 0",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pode_transferencia INTEGER DEFAULT 0",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pode_historico INTEGER DEFAULT 0",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pode_usuarios INTEGER DEFAULT 0",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pode_editar_estoque INTEGER DEFAULT 0",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pode_excluir_estoque INTEGER DEFAULT 0",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pode_logs INTEGER DEFAULT 0"
        ]

        for sql in colunas_usuarios:
            try:
                cursor.execute(sql)
            except Exception:
                conn.rollback()
                cursor = conn.cursor()

        try:
            cursor.execute("""
            ALTER TABLE estoque
            ADD COLUMN IF NOT EXISTS id SERIAL
            """)
        except Exception:
            conn.rollback()
            cursor = conn.cursor()

        try:
            cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'estoque_pkey'
                ) THEN
                    BEGIN
                        ALTER TABLE estoque ADD PRIMARY KEY (id);
                    EXCEPTION
                        WHEN others THEN
                            NULL;
                    END;
                END IF;
            END
            $$;
            """)
        except Exception:
            conn.rollback()
            cursor = conn.cursor()

        try:
            cursor.execute("""
            ALTER TABLE transferencias
            ADD COLUMN IF NOT EXISTS id SERIAL
            """)
        except Exception:
            conn.rollback()
            cursor = conn.cursor()

        try:
            cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'transferencias_pkey'
                ) THEN
                    BEGIN
                        ALTER TABLE transferencias ADD PRIMARY KEY (id);
                    EXCEPTION
                        WHEN others THEN
                            NULL;
                    END;
                END IF;
            END
            $$;
            """)
        except Exception:
            conn.rollback()
            cursor = conn.cursor()

        cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", ("admin",))
        admin = cursor.fetchone()
        if not admin:
            cursor.execute("""
            INSERT INTO usuarios (
                usuario, senha, cargo, online, ativo,
                pode_estoque, pode_transferencia, pode_historico,
                pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                "admin",
                generate_password_hash("admin123"),
                "admin",
                0,
                1,
                1, 1, 1, 1, 1, 1, 1
            ))
        else:
            cursor.execute("""
            UPDATE usuarios
            SET cargo='admin',
                ativo=1,
                pode_estoque=1,
                pode_transferencia=1,
                pode_historico=1,
                pode_usuarios=1,
                pode_editar_estoque=1,
                pode_excluir_estoque=1,
                pode_logs=1
            WHERE usuario='admin'
            """)

        conn.commit()
    except Exception as e:
        print("Erro ao criar banco:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

criar_banco()

# ================= TOPO =================
def topo():
    return """
    <div style="background:#020617;padding:15px;color:#38bdf8;font-family:'Share Tech Mono', monospace;border-bottom:2px solid #0ea5e9;">
        <b style="font-size:18px;">⚡ KBSISTEMAS</b> |
        <a href="/painel">Painel</a> |
        <a href="/estoque">Estoque</a> |
        <a href="/transferencia">Transferência</a> |
        <a href="/historico">Histórico</a> |
        <a href="/usuarios">Usuários</a> |
        <a href="/logs">Logs</a> |
        <a href="/logout" style="color:#f87171;">Sair</a>
    </div>
    """

# ================= CONTAINER =================
def container(c):
    return f"""
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">
    </head>
    """ + topo() + f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    body {{
        margin:0;
        font-family:'Share Tech Mono', monospace;
        background:#020617;
        color:#7dd3fc;
    }}

    .overlay {{
        padding:20px;
        min-height:100vh;
        background:
            linear-gradient(rgba(2,6,23,0.84), rgba(2,6,23,0.94)),
            url('/static/hacker.png') no-repeat center center fixed;
        background-size: cover;
    }}

    a {{
        color:#38bdf8;
        text-decoration:none;
        margin-right:15px;
    }}

    a:hover {{
        text-decoration:underline;
        color:#7dd3fc;
    }}

    input, button, select, textarea {{
        padding:10px;
        margin:5px 0;
        border-radius:8px;
        border:1px solid #0ea5e9;
        background:#020617;
        color:#7dd3fc;
        font-family:'Share Tech Mono', monospace;
    }}

    textarea {{
        width:100%;
        min-height:80px;
    }}

    input[type="checkbox"] {{
        width:auto;
        transform:scale(1.2);
        margin-right:8px;
    }}

    button {{
        cursor:pointer;
        transition:0.3s;
    }}

    button:hover {{
        background:#0ea5e9;
        color:#03111f;
        font-weight:bold;
        box-shadow:0 0 14px rgba(14,165,233,0.35);
    }}

    table {{
        width:100%;
        background:rgba(2,6,23,0.86);
        border-collapse:collapse;
        margin-top:15px;
    }}

    th, td {{
        padding:10px;
        border:1px solid #0ea5e9;
        text-align:left;
        vertical-align:top;
    }}

    th {{
        background:#0f172a;
        color:#7dd3fc;
    }}

    .card {{
        background:rgba(2,6,23,0.86);
        border:1px solid #0ea5e9;
        border-radius:14px;
        padding:20px;
        margin-bottom:20px;
        box-shadow:0 0 18px rgba(14,165,233,0.18);
        color:#dbeafe;
    }}

    .cards {{
        display:grid;
        grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));
        gap:15px;
        margin-top:20px;
    }}

    .mini-card {{
        background:rgba(2,6,23,0.86);
        border:1px solid #0ea5e9;
        border-radius:14px;
        padding:20px;
        box-shadow:0 0 12px rgba(14,165,233,0.16);
        color:#dbeafe;
    }}

    .mensagem {{
        margin-top:10px;
        font-weight:bold;
        color:#7dd3fc;
    }}

    .erro {{
        color:#f87171;
        font-weight:bold;
    }}

    .sucesso {{
        color:#4ade80;
        font-weight:bold;
    }}

    .btn-danger {{
        color:#f87171;
        border-color:#f87171;
    }}

    .btn-danger:hover {{
        background:#f87171;
        color:#020617;
    }}

    .btn-warning {{
        color:#facc15;
        border-color:#facc15;
    }}

    .btn-warning:hover {{
        background:#facc15;
        color:#020617;
    }}

    .btn-edit {{
        color:#7dd3fc;
        border:1px solid #7dd3fc;
        padding:6px 10px;
        border-radius:8px;
        display:inline-block;
    }}

    .btn-edit:hover {{
        background:#7dd3fc;
        color:#020617;
    }}

    .permissoes-box {{
        display:grid;
        grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));
        gap:8px;
        margin-top:10px;
    }}

    .perm-item {{
        background:rgba(15,23,42,0.7);
        padding:8px;
        border-radius:8px;
        border:1px solid #0ea5e9;
    }}
    </style>

    <div class="overlay">
        {c}
    </div>
    """

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
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

                    cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s",
                                   (request.form["user"],))
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
            if conn:
                conn.close()

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
        overflow: hidden;
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
        padding: 20px;
    }}

    .login-box {{
        width: 390px;
        background: rgba(0, 20, 20, 0.30);
        border: 2px solid rgba(0, 255, 170, 0.7);
        border-radius: 18px;
        padding: 35px 30px;
        box-shadow: 0 0 25px rgba(0, 255, 170, 0.35);
        backdrop-filter: blur(6px);
    }}

    .titulo {{
        text-align: center;
        margin-bottom: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 34px;
        color: #7df9ff;
        letter-spacing: 3px;
        text-shadow: 0 0 12px rgba(0,255,255,0.7);
    }}

    .subtitulo {{
        text-align: center;
        margin-bottom: 24px;
        color: #9afcff;
        font-size: 14px;
    }}

    .campo {{
        margin-bottom: 16px;
    }}

    .campo label {{
        display: block;
        margin-bottom: 8px;
        color: #7df9ff;
        font-size: 14px;
    }}

    .campo input {{
        width: 100%;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid rgba(0,255,255,0.65);
        background: rgba(0,0,0,0.45);
        color: #dff;
        outline: none;
        font-size: 16px;
        font-family: 'Share Tech Mono', monospace;
    }}

    .campo input:focus {{
        box-shadow: 0 0 12px rgba(0,255,255,0.35);
        border-color: #00ffff;
    }}

    .campo input::placeholder {{
        color: #86d9d9;
    }}

    button {{
        width: 100%;
        padding: 14px;
        border: 1px solid rgba(0,255,255,0.8);
        border-radius: 10px;
        background: rgba(0, 255, 255, 0.10);
        color: #7df9ff;
        font-size: 18px;
        font-family: 'Orbitron', sans-serif;
        cursor: pointer;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(0,255,255,0.2);
    }}

    button:hover {{
        background: rgba(0,255,255,0.25);
        box-shadow: 0 0 20px rgba(0,255,255,0.4);
        color: white;
    }}

    .erro {{
        margin-top: 16px;
        text-align: center;
        color: #ff6b6b;
        min-height: 20px;
        font-size: 14px;
    }}
    </style>

    <canvas id="matrix"></canvas>

    <div class="login-wrapper">
        <div class="login-box">
            <div class="titulo">KBSISTEMAS</div>
            <div class="subtitulo">Acesso ao sistema interno</div>

            <form method="POST">
                <div class="campo">
                    <label>Usuário</label>
                    <input name="user" placeholder="Digite seu usuário" required>
                </div>

                <div class="campo">
                    <label>Senha</label>
                    <input name="senha" type="password" placeholder="Digite sua senha" required>
                </div>

                <button>LOGIN</button>
            </form>

            <div class="erro">{erro}</div>
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

        ctx.fillStyle = "#00d9ff";
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

# ================= PAINEL =================
@app.route("/painel")
def painel():
    if "user" not in session:
        return redirect("/")

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM estoque")
        total_qtd = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transferencias")
        total_transferencias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE online=1")
        usuarios_online = cursor.fetchone()[0]

        return container(f"""
        <div class="card">
            <h2>🖥️ PAINEL DO SISTEMA</h2>
            <p>Bem-vindo, <b>{session["user"]}</b> | Cargo: <b>{session.get("cargo", "")}</b></p>
            <p>Este sistema permite controlar o estoque, registrar transferências, acompanhar o histórico, gerenciar usuários e auditar ações com logs.</p>
        </div>

        <div class="cards">
            <div class="mini-card">
                <h3>📦 Produtos cadastrados</h3>
                <p style="font-size:28px;">{total_produtos}</p>
            </div>
            <div class="mini-card">
                <h3>🔢 Quantidade total</h3>
                <p style="font-size:28px;">{total_qtd}</p>
            </div>
            <div class="mini-card">
                <h3>🔄 Transferências</h3>
                <p style="font-size:28px;">{total_transferencias}</p>
            </div>
            <div class="mini-card">
                <h3>🟢 Usuários online</h3>
                <p style="font-size:28px;">{usuarios_online}</p>
            </div>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro no painel: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= ESTOQUE =================
@app.route("/estoque", methods=["GET", "POST"])
def estoque():
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_estoque"):
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        if request.method == "POST":
            produto = request.form["produto"].strip()
            qtd = request.form["qtd"].strip()
            categoria = request.form["categoria"].strip()

            if not produto or not qtd or not categoria:
                mensagem = "Preencha todos os campos."
            else:
                try:
                    qtd_int = int(qtd)
                    if qtd_int < 0:
                        mensagem = "A quantidade não pode ser negativa."
                    else:
                        cursor.execute("""
                        INSERT INTO estoque (produto, quantidade, categoria)
                        VALUES (%s, %s, %s)
                        """, (produto, qtd_int, categoria))
                        conn.commit()
                        mensagem = "Produto adicionado com sucesso."
                        registrar_log(session["user"], "adicionar_estoque", f"Produto: {produto} | Qtd: {qtd_int} | Categoria: {categoria}")
                except:
                    mensagem = "Quantidade inválida."

        busca = request.args.get("busca", "").strip()

        if busca:
            cursor.execute("""
            SELECT id, produto, quantidade, categoria
            FROM estoque
            WHERE produto ILIKE %s OR categoria ILIKE %s
            ORDER BY id DESC
            """, (f"%{busca}%", f"%{busca}%"))
        else:
            cursor.execute("""
            SELECT id, produto, quantidade, categoria
            FROM estoque
            ORDER BY id DESC
            """)

        dados = cursor.fetchall()

        tabela = ""
        for i, p, q, c in dados:
            acoes = ""
            if tem_permissao("pode_editar_estoque"):
                acoes += f'<a href="/editar_estoque/{i}" class="btn-warning">Editar</a>'
            if tem_permissao("pode_excluir_estoque"):
                acoes += f'<a href="/excluir_estoque/{i}" class="btn-danger" onclick="return confirm(\'Deseja excluir este item?\')">Excluir</a>'
            if not acoes:
                acoes = "Sem permissão"

            tabela += f"""
            <tr>
                <td>{i}</td>
                <td>{p}</td>
                <td>{q}</td>
                <td>{c}</td>
                <td>{acoes}</td>
            </tr>
            """

        return container(f"""
        <div class="card">
            <h2>📦 ESTOQUE</h2>

            <form method="POST">
                <input name="produto" placeholder="Produto" required>
                <input name="qtd" placeholder="Quantidade" required>
                <input name="categoria" placeholder="Categoria" required>
                <button>Adicionar</button>
            </form>

            <div class="mensagem">{mensagem}</div>
        </div>

        <div class="card">
            <form method="GET">
                <input name="busca" placeholder="Buscar por produto ou categoria" value="{busca}">
                <button>Pesquisar</button>
                <a href="/estoque">Limpar</a>
            </form>

            <table>
                <tr>
                    <th>ID</th>
                    <th>Produto</th>
                    <th>Qtd</th>
                    <th>Categoria</th>
                    <th>Ações</th>
                </tr>
                {tabela}
            </table>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro no estoque: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= EDITAR ESTOQUE =================
@app.route("/editar_estoque/<int:item_id>", methods=["GET", "POST"])
def editar_estoque(item_id):
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_editar_estoque"):
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque WHERE id=%s", (item_id,))
        dado = cursor.fetchone()

        if not dado:
            return container("<div class='card'><h2>Item não encontrado.</h2></div>")

        i, p_antigo, q_antigo, c_antigo = dado

        if request.method == "POST":
            produto = request.form["produto"].strip()
            qtd = request.form["qtd"].strip()
            categoria = request.form["categoria"].strip()

            try:
                qtd_int = int(qtd)
                if qtd_int < 0:
                    mensagem = "A quantidade não pode ser negativa."
                else:
                    cursor.execute("""
                    UPDATE estoque
                    SET produto=%s, quantidade=%s, categoria=%s
                    WHERE id=%s
                    """, (produto, qtd_int, categoria, item_id))
                    conn.commit()
                    registrar_log(
                        session["user"],
                        "editar_estoque",
                        f"ID: {item_id} | Antes: {p_antigo}/{q_antigo}/{c_antigo} | Depois: {produto}/{qtd_int}/{categoria}"
                    )
                    return redirect("/estoque")
            except:
                mensagem = "Quantidade inválida."

        return container(f"""
        <div class="card">
            <h2>✏️ EDITAR ESTOQUE</h2>
            <form method="POST">
                <input name="produto" value="{p_antigo}" placeholder="Produto" required>
                <input name="qtd" value="{q_antigo}" placeholder="Quantidade" required>
                <input name="categoria" value="{c_antigo}" placeholder="Categoria" required>
                <button>Salvar alterações</button>
            </form>
            <div class="mensagem">{mensagem}</div>
            <p><a href="/estoque">⬅ Voltar</a></p>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro ao editar estoque: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= EXCLUIR ESTOQUE =================
@app.route("/excluir_estoque/<int:item_id>")
def excluir_estoque(item_id):
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_excluir_estoque"):
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT produto, quantidade, categoria FROM estoque WHERE id=%s", (item_id,))
        dado = cursor.fetchone()

        cursor.execute("DELETE FROM estoque WHERE id=%s", (item_id,))
        conn.commit()

        if dado:
            registrar_log(session["user"], "excluir_estoque", f"ID: {item_id} | Produto: {dado[0]} | Qtd: {dado[1]} | Categoria: {dado[2]}")

        return redirect("/estoque")
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro ao excluir item: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= TRANSFERÊNCIA =================
@app.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_transferencia"):
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        if request.method == "POST":
            produto = request.form["produto"].strip()
            qtd = request.form["qtd"].strip()
            origem = request.form["origem"].strip()
            destino = request.form["destino"].strip()

            try:
                qtd_int = int(qtd)

                if qtd_int <= 0:
                    mensagem = "Informe uma quantidade válida."
                else:
                    cursor.execute("SELECT id, quantidade FROM estoque WHERE produto=%s ORDER BY id LIMIT 1", (produto,))
                    item = cursor.fetchone()

                    if not item:
                        mensagem = "Produto não encontrado no estoque."
                    else:
                        estoque_id, qtd_atual = item

                        if qtd_int > qtd_atual:
                            mensagem = "Quantidade insuficiente no estoque."
                        else:
                            nova_qtd = qtd_atual - qtd_int

                            cursor.execute("""
                            UPDATE estoque
                            SET quantidade=%s
                            WHERE id=%s
                            """, (nova_qtd, estoque_id))

                            cursor.execute("""
                            INSERT INTO transferencias (produto, quantidade, origem, destino, usuario)
                            VALUES (%s,%s,%s,%s,%s)
                            """, (
                                produto,
                                qtd_int,
                                origem,
                                destino,
                                session["user"]
                            ))

                            conn.commit()
                            mensagem = "Transferência realizada com sucesso."
                            registrar_log(session["user"], "transferencia", f"Produto: {produto} | Qtd: {qtd_int} | Origem: {origem} | Destino: {destino}")
            except:
                mensagem = "Quantidade inválida."

        return container(f"""
        <div class="card">
            <h2>🔄 TRANSFERÊNCIA</h2>

            <form method="POST">
                <input name="produto" placeholder="Produto" required>
                <input name="qtd" placeholder="Quantidade" required>
                <input name="origem" placeholder="Origem" required>
                <input name="destino" placeholder="Destino" required>
                <button>Transferir</button>
            </form>

            <div class="mensagem">{mensagem}</div>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro na transferência: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= HISTÓRICO =================
@app.route("/historico")
def historico():
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_historico"):
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT produto, quantidade, origem, destino, usuario, data
        FROM transferencias
        ORDER BY data DESC
        """)
        dados = cursor.fetchall()

        tabela = ""
        for p, q, o, d, u, dt in dados:
            tabela += f"""
            <tr>
                <td>{p}</td>
                <td>{q}</td>
                <td>{o}</td>
                <td>{d}</td>
                <td>{u}</td>
                <td>{dt}</td>
            </tr>
            """

        return container(f"""
        <div class="card">
            <h2>📜 HISTÓRICO DE TRANSFERÊNCIAS</h2>

            <table>
                <tr>
                    <th>Produto</th>
                    <th>Qtd</th>
                    <th>Origem</th>
                    <th>Destino</th>
                    <th>Usuário</th>
                    <th>Data</th>
                </tr>
                {tabela}
            </table>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro no histórico: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= LOGS =================
@app.route("/logs")
def logs():
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_logs"):
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, usuario, acao, detalhes, data
        FROM logs
        ORDER BY data DESC, id DESC
        LIMIT 300
        """)
        dados = cursor.fetchall()

        tabela = ""
        for i, u, a, d, dt in dados:
            tabela += f"""
            <tr>
                <td>{i}</td>
                <td>{u}</td>
                <td>{a}</td>
                <td>{d}</td>
                <td>{dt}</td>
            </tr>
            """

        return container(f"""
        <div class="card">
            <h2>📋 LOGS DO SISTEMA</h2>
            <p>Aqui ficam registradas as ações importantes realizadas no sistema.</p>

            <table>
                <tr>
                    <th>ID</th>
                    <th>Usuário</th>
                    <th>Ação</th>
                    <th>Detalhes</th>
                    <th>Data</th>
                </tr>
                {tabela}
            </table>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro nos logs: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_usuarios"):
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        if request.method == "POST":
            try:
                user = request.form["user"].strip()
                senha = request.form["senha"].strip()
                cargo = request.form["cargo"].strip()

                if cargo == "admin":
                    ativo = 1
                    pode_estoque = 1
                    pode_transferencia = 1
                    pode_historico = 1
                    pode_usuarios = 1
                    pode_editar_estoque = 1
                    pode_excluir_estoque = 1
                    pode_logs = 1
                else:
                    ativo = 1 if request.form.get("ativo") == "1" else 0
                    pode_estoque = 1 if request.form.get("pode_estoque") == "1" else 0
                    pode_transferencia = 1 if request.form.get("pode_transferencia") == "1" else 0
                    pode_historico = 1 if request.form.get("pode_historico") == "1" else 0
                    pode_usuarios = 1 if request.form.get("pode_usuarios") == "1" else 0
                    pode_editar_estoque = 1 if request.form.get("pode_editar_estoque") == "1" else 0
                    pode_excluir_estoque = 1 if request.form.get("pode_excluir_estoque") == "1" else 0
                    pode_logs = 1 if request.form.get("pode_logs") == "1" else 0

                cursor.execute("""
                INSERT INTO usuarios (
                    usuario, senha, cargo, ativo,
                    pode_estoque, pode_transferencia, pode_historico,
                    pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    user,
                    generate_password_hash(senha),
                    cargo,
                    ativo,
                    pode_estoque,
                    pode_transferencia,
                    pode_historico,
                    pode_usuarios,
                    pode_editar_estoque,
                    pode_excluir_estoque,
                    pode_logs
                ))
                conn.commit()
                mensagem = "Usuário criado com sucesso."
                registrar_log(session["user"], "criar_usuario", f"Usuário criado: {user} | Cargo: {cargo}")
            except Exception:
                conn.rollback()
                mensagem = "Não foi possível criar o usuário. Talvez ele já exista."

        cursor.execute("""
        SELECT usuario, cargo, online, ativo,
               pode_estoque, pode_transferencia, pode_historico,
               pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
        FROM usuarios
        ORDER BY usuario
        """)
        dados = cursor.fetchall()

        tabela = ""
        for u, c, o, ativo, pe, pt, ph, pu, ped, pex, pl in dados:
            status_online = "🟢 Online" if o else "🔴 Offline"
            status_ativo = "✅ Ativo" if ativo else "⛔ Inativo"

            permissoes = []
            if pe: permissoes.append("Estoque")
            if pt: permissoes.append("Transferência")
            if ph: permissoes.append("Histórico")
            if pu: permissoes.append("Usuários")
            if ped: permissoes.append("Editar estoque")
            if pex: permissoes.append("Excluir estoque")
            if pl: permissoes.append("Logs")

            texto_permissoes = ", ".join(permissoes) if permissoes else "Nenhuma"

            acoes = ""
            if u != "admin":
                acoes += f'<a href="/editar_usuario/{u}" class="btn-edit">Editar</a>'
                acoes += f'<a href="/alterar_senha/{u}" class="btn-warning">Trocar senha</a>'
                acoes += f'<a href="/excluir_usuario/{u}" class="btn-danger" onclick="return confirm(\'Deseja excluir este usuário?\')">Excluir</a>'
            else:
                acoes = "Protegido"

            tabela += f"""
            <tr>
                <td>{u}</td>
                <td>{c}</td>
                <td>{status_online}<br>{status_ativo}</td>
                <td>{texto_permissoes}</td>
                <td>{acoes}</td>
            </tr>
            """

        return container(f"""
        <div class="card">
            <h2>👤 USUÁRIOS</h2>

            <form method="POST">
                <input name="user" placeholder="Usuário" required>
                <input name="senha" placeholder="Senha" required>

                <select name="cargo" required>
                    <option value="operador">operador</option>
                    <option value="admin">admin</option>
                </select>

                <div class="permissoes-box">
                    <label class="perm-item"><input type="checkbox" name="ativo" value="1" checked>Usuário ativo</label>
                    <label class="perm-item"><input type="checkbox" name="pode_estoque" value="1">Acessar estoque</label>
                    <label class="perm-item"><input type="checkbox" name="pode_transferencia" value="1">Acessar transferência</label>
                    <label class="perm-item"><input type="checkbox" name="pode_historico" value="1">Acessar histórico</label>
                    <label class="perm-item"><input type="checkbox" name="pode_usuarios" value="1">Acessar usuários</label>
                    <label class="perm-item"><input type="checkbox" name="pode_editar_estoque" value="1">Editar estoque</label>
                    <label class="perm-item"><input type="checkbox" name="pode_excluir_estoque" value="1">Excluir estoque</label>
                    <label class="perm-item"><input type="checkbox" name="pode_logs" value="1">Acessar logs</label>
                </div>

                <button>Criar</button>
            </form>

            <div class="mensagem">{mensagem}</div>
        </div>

        <div class="card">
            <table>
                <tr>
                    <th>Usuário</th>
                    <th>Cargo</th>
                    <th>Status</th>
                    <th>Permissões</th>
                    <th>Ações</th>
                </tr>
                {tabela}
            </table>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro nos usuários: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= EDITAR USUÁRIO =================
@app.route("/editar_usuario/<usuario_alvo>", methods=["GET", "POST"])
def editar_usuario(usuario_alvo):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    if usuario_alvo == "admin":
        return container("""
        <div class="card">
            <h2 class="erro">⛔ O usuário admin não pode ser editado por esta tela.</h2>
            <p><a href="/usuarios">⬅ Voltar</a></p>
        </div>
        """)

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        cursor.execute("""
        SELECT usuario, cargo, ativo,
               pode_estoque, pode_transferencia, pode_historico,
               pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
        FROM usuarios
        WHERE usuario=%s
        """, (usuario_alvo,))
        dado = cursor.fetchone()

        if not dado:
            return container("<div class='card'><h2>Usuário não encontrado.</h2></div>")

        u, c_antigo, ativo_antigo, pe_antigo, pt_antigo, ph_antigo, pu_antigo, ped_antigo, pex_antigo, pl_antigo = dado

        if request.method == "POST":
            cargo = request.form["cargo"].strip()

            if cargo == "admin":
                ativo = 1
                pode_estoque = 1
                pode_transferencia = 1
                pode_historico = 1
                pode_usuarios = 1
                pode_editar_estoque = 1
                pode_excluir_estoque = 1
                pode_logs = 1
            else:
                ativo = 1 if request.form.get("ativo") == "1" else 0
                pode_estoque = 1 if request.form.get("pode_estoque") == "1" else 0
                pode_transferencia = 1 if request.form.get("pode_transferencia") == "1" else 0
                pode_historico = 1 if request.form.get("pode_historico") == "1" else 0
                pode_usuarios = 1 if request.form.get("pode_usuarios") == "1" else 0
                pode_editar_estoque = 1 if request.form.get("pode_editar_estoque") == "1" else 0
                pode_excluir_estoque = 1 if request.form.get("pode_excluir_estoque") == "1" else 0
                pode_logs = 1 if request.form.get("pode_logs") == "1" else 0

            cursor.execute("""
            UPDATE usuarios
            SET cargo=%s,
                ativo=%s,
                pode_estoque=%s,
                pode_transferencia=%s,
                pode_historico=%s,
                pode_usuarios=%s,
                pode_editar_estoque=%s,
                pode_excluir_estoque=%s,
                pode_logs=%s
            WHERE usuario=%s
            """, (
                cargo,
                ativo,
                pode_estoque,
                pode_transferencia,
                pode_historico,
                pode_usuarios,
                pode_editar_estoque,
                pode_excluir_estoque,
                pode_logs,
                usuario_alvo
            ))
            conn.commit()
            mensagem = "Usuário atualizado com sucesso."
            registrar_log(
                session["user"],
                "editar_usuario",
                f"Usuário: {usuario_alvo} | Cargo: {c_antigo} -> {cargo} | Ativo: {ativo_antigo} -> {ativo}"
            )

            cursor.execute("""
            SELECT usuario, cargo, ativo,
                   pode_estoque, pode_transferencia, pode_historico,
                   pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
            FROM usuarios
            WHERE usuario=%s
            """, (usuario_alvo,))
            dado = cursor.fetchone()
            u, c_antigo, ativo_antigo, pe_antigo, pt_antigo, ph_antigo, pu_antigo, ped_antigo, pex_antigo, pl_antigo = dado

        checked_ativo = "checked" if ativo_antigo else ""
        checked_pe = "checked" if pe_antigo else ""
        checked_pt = "checked" if pt_antigo else ""
        checked_ph = "checked" if ph_antigo else ""
        checked_pu = "checked" if pu_antigo else ""
        checked_ped = "checked" if ped_antigo else ""
        checked_pex = "checked" if pex_antigo else ""
        checked_pl = "checked" if pl_antigo else ""

        selected_admin = "selected" if c_antigo == "admin" else ""
        selected_operador = "selected" if c_antigo == "operador" else ""

        return container(f"""
        <div class="card">
            <h2>🛠️ EDITAR USUÁRIO</h2>
            <p>Usuário: <b>{u}</b></p>

            <form method="POST">
                <select name="cargo" required>
                    <option value="operador" {selected_operador}>operador</option>
                    <option value="admin" {selected_admin}>admin</option>
                </select>

                <div class="permissoes-box">
                    <label class="perm-item"><input type="checkbox" name="ativo" value="1" {checked_ativo}>Usuário ativo</label>
                    <label class="perm-item"><input type="checkbox" name="pode_estoque" value="1" {checked_pe}>Acessar estoque</label>
                    <label class="perm-item"><input type="checkbox" name="pode_transferencia" value="1" {checked_pt}>Acessar transferência</label>
                    <label class="perm-item"><input type="checkbox" name="pode_historico" value="1" {checked_ph}>Acessar histórico</label>
                    <label class="perm-item"><input type="checkbox" name="pode_usuarios" value="1" {checked_pu}>Acessar usuários</label>
                    <label class="perm-item"><input type="checkbox" name="pode_editar_estoque" value="1" {checked_ped}>Editar estoque</label>
                    <label class="perm-item"><input type="checkbox" name="pode_excluir_estoque" value="1" {checked_pex}>Excluir estoque</label>
                    <label class="perm-item"><input type="checkbox" name="pode_logs" value="1" {checked_pl}>Acessar logs</label>
                </div>

                <button>Salvar alterações</button>
            </form>

            <div class="mensagem">{mensagem}</div>
            <p><a href="/usuarios">⬅ Voltar</a></p>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro ao editar usuário: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= ALTERAR SENHA =================
@app.route("/alterar_senha/<usuario_alvo>", methods=["GET", "POST"])
def alterar_senha(usuario_alvo):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        if request.method == "POST":
            nova_senha = request.form["nova_senha"].strip()

            if not nova_senha:
                mensagem = "Digite a nova senha."
            else:
                cursor.execute("""
                UPDATE usuarios
                SET senha=%s
                WHERE usuario=%s
                """, (generate_password_hash(nova_senha), usuario_alvo))
                conn.commit()
                mensagem = "Senha alterada com sucesso."
                registrar_log(session["user"], "alterar_senha", f"Senha alterada para o usuário: {usuario_alvo}")

        return container(f"""
        <div class="card">
            <h2>🔑 ALTERAR SENHA</h2>
            <p>Usuário: <b>{usuario_alvo}</b></p>

            <form method="POST">
                <input name="nova_senha" placeholder="Nova senha" required>
                <button>Salvar nova senha</button>
            </form>

            <div class="mensagem">{mensagem}</div>
            <p><a href="/usuarios">⬅ Voltar</a></p>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro ao alterar senha: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= EXCLUIR USUÁRIO =================
@app.route("/excluir_usuario/<usuario_alvo>")
def excluir_usuario(usuario_alvo):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    if usuario_alvo == "admin":
        return container("""
        <div class="card">
            <h2 class="erro">⛔ O usuário admin não pode ser excluído.</h2>
            <p><a href="/usuarios">⬅ Voltar</a></p>
        </div>
        """)

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario_alvo,))
        conn.commit()
        registrar_log(session["user"], "excluir_usuario", f"Usuário excluído: {usuario_alvo}")
        return redirect("/usuarios")
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro ao excluir usuário: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    usuario = session.get("user")

    if "user" in session:
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("UPDATE usuarios SET online=0 WHERE usuario=%s",
                           (session["user"],))
            conn.commit()
        except Exception as e:
            print("Erro no logout:", e)
        finally:
            if conn:
                conn.close()

    if usuario:
        registrar_log(usuario, "logout", "Usuário saiu do sistema")

    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
