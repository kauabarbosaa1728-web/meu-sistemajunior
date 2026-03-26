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
            online INTEGER DEFAULT 0
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
            INSERT INTO usuarios (usuario, senha, cargo, online)
            VALUES (%s, %s, %s, %s)
            """, (
                "admin",
                generate_password_hash("admin123"),
                "admin",
                0
            ))

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
        <a href="/logout" style="color:#f87171;">Sair</a>
    </div>
    """

# ================= CONTAINER =================
def container(c):
    return topo() + f"""
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

    input, button, select {{
        padding:10px;
        margin:5px 0;
        border-radius:8px;
        border:1px solid #0ea5e9;
        background:#020617;
        color:#7dd3fc;
        font-family:'Share Tech Mono', monospace;
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

            cursor.execute("SELECT senha, cargo FROM usuarios WHERE usuario=%s",
                           (request.form["user"],))
            user = cursor.fetchone()

            if user and check_password_hash(user[0], request.form["senha"]):
                session["user"] = request.form["user"]
                session["cargo"] = user[1]

                cursor.execute("UPDATE usuarios SET online=1 WHERE usuario=%s",
                               (request.form["user"],))
                conn.commit()

                return redirect("/painel")
            else:
                erro = "Usuário ou senha inválidos"
        except Exception as e:
            erro = f"Erro ao fazer login: {e}"
        finally:
            if conn:
                conn.close()

    return f"""
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
            <p>Este sistema permite controlar o estoque, registrar transferências, acompanhar o histórico e gerenciar usuários.</p>
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
            tabela += f"""
            <tr>
                <td>{i}</td>
                <td>{p}</td>
                <td>{q}</td>
                <td>{c}</td>
                <td>
                    <a href="/editar_estoque/{i}" class="btn-warning">Editar</a>
                    <a href="/excluir_estoque/{i}" class="btn-danger" onclick="return confirm('Deseja excluir este item?')">Excluir</a>
                </td>
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

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

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
                    return redirect("/estoque")
            except:
                mensagem = "Quantidade inválida."

        cursor.execute("SELECT id, produto, quantidade, categoria FROM estoque WHERE id=%s", (item_id,))
        dado = cursor.fetchone()

        if not dado:
            return container("<div class='card'><h2>Item não encontrado.</h2></div>")

        i, p, q, c = dado

        return container(f"""
        <div class="card">
            <h2>✏️ EDITAR ESTOQUE</h2>
            <form method="POST">
                <input name="produto" value="{p}" placeholder="Produto" required>
                <input name="qtd" value="{q}" placeholder="Quantidade" required>
                <input name="categoria" value="{c}" placeholder="Categoria" required>
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

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estoque WHERE id=%s", (item_id,))
        conn.commit()
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

# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if session.get("cargo") != "admin":
        return "Sem permissão"

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        if request.method == "POST":
            try:
                cursor.execute("""
                INSERT INTO usuarios (usuario, senha, cargo)
                VALUES (%s,%s,%s)
                """, (
                    request.form["user"],
                    generate_password_hash(request.form["senha"]),
                    request.form["cargo"]
                ))
                conn.commit()
                mensagem = "Usuário criado com sucesso."
            except Exception:
                conn.rollback()
                mensagem = "Não foi possível criar o usuário. Talvez ele já exista."

        cursor.execute("SELECT usuario, cargo, online FROM usuarios ORDER BY usuario")
        dados = cursor.fetchall()

        tabela = ""
        for u, c, o in dados:
            status = "🟢 Online" if o else "🔴 Offline"
            tabela += f"<tr><td>{u}</td><td>{c}</td><td>{status}</td></tr>"

        return container(f"""
        <div class="card">
            <h2>👤 USUÁRIOS</h2>

            <form method="POST">
                <input name="user" placeholder="Usuário" required>
                <input name="senha" placeholder="Senha" required>
                <input name="cargo" placeholder="Cargo" required>
                <button>Criar</button>
            </form>

            <div class="mensagem">{mensagem}</div>
        </div>

        <div class="card">
            <table>
                <tr><th>Usuário</th><th>Cargo</th><th>Status</th></tr>
                {tabela}
            </table>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro nos usuários: {e}</h2></div>')
    finally:
        if conn:
            conn.close()

# ================= LOGOUT =================
@app.route("/logout")
def logout():
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

    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
