from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash
from banco import conectar, devolver_conexao, registrar_log
from layout import container, acesso_negado
from datetime import datetime, timedelta

usuarios_bp = Blueprint("usuarios_bp", __name__)

# ================= USUÁRIOS =================
@usuarios_bp.route("/", methods=["GET", "POST"])
def usuarios():
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        # CRIAR USUARIO
        if request.method == "POST":
            try:
                user = request.form["user"].strip()
                senha = request.form["senha"].strip()
                cargo = request.form["cargo"].strip()
                email = request.form.get("email", "").strip()
                nome_empresa = request.form.get("nome_empresa", "").strip()
                plano = request.form.get("plano", "basico").strip().lower()

                cursor.execute("""
                INSERT INTO usuarios (
                    usuario, senha, cargo, ativo, email, plano, nome_empresa
                )
                VALUES (%s,%s,%s,1,%s,%s,%s)
                """, (
                    user,
                    generate_password_hash(senha),
                    cargo,
                    email,
                    plano,
                    nome_empresa
                ))

                conn.commit()
                mensagem = "Usuário criado com sucesso."
            except:
                conn.rollback()
                mensagem = "Erro ao criar usuário."

        # BUSCAR DADOS
        cursor.execute("""
        SELECT usuario, cargo, online, ativo, email, plano, nome_empresa
        FROM usuarios
        ORDER BY usuario
        """)
        dados = cursor.fetchall()

        cursor.execute("SELECT usuario, status FROM pagamentos")
        pagamentos = dict(cursor.fetchall())

        tabela = ""

        for u, c, o, ativo, email, plano, nome_empresa in dados:
            status_online = "🟢 Online" if o else "🔴 Offline"

            status_pagamento = pagamentos.get(u, "bloqueado")
            cor = "#00ff00" if status_pagamento == "pago" else "red"
            texto_status = "PAGO" if status_pagamento == "pago" else "BLOQUEADO"

            if u != "admin":
                acoes = f'''
                <a href="/editar_usuario/{u}">Editar</a> |
                <a href="/alterar_senha/{u}">Senha</a> |
                <a href="/mudar_plano/{u}">Plano</a> |
                <a href="/excluir_usuario/{u}">Excluir</a><br><br>

                <form action="/usuarios/liberar_usuario/{u}" method="POST" style="display:inline;">
                    <input type="number" name="dias" placeholder="Dias" required style="width:60px;">
                    <button style="background:#00ff00;color:#000;">💸 Liberar</button>
                </form>

                <form action="/usuarios/bloquear_usuario/{u}" method="POST" style="display:inline;">
                    <input type="number" name="dias" placeholder="Dias" required style="width:60px;">
                    <button style="background:red;color:#fff;">🔒 Bloquear</button>
                </form>
                '''
            else:
                acoes = "Protegido"

            tabela += f"""
            <tr>
                <td>{u}</td>
                <td>{c}</td>
                <td>{email or '-'}</td>
                <td>{nome_empresa or '-'}</td>
                <td>{plano}</td>
                <td>{status_online}</td>
                <td style="color:{cor};font-weight:bold;">{texto_status}</td>
                <td>{acoes}</td>
            </tr>
            """

        return container(f"""
        <div class="card">
            <h2>👤 USUÁRIOS</h2>

            <form method="POST">
                <input name="user" placeholder="Usuário" required>
                <input name="senha" placeholder="Senha" required>
                <input name="email" placeholder="E-mail">
                <input name="nome_empresa" placeholder="Empresa">

                <select name="cargo">
                    <option value="operador">operador</option>
                    <option value="admin">admin</option>
                </select>

                <select name="plano">
                    <option value="basico">basico</option>
                    <option value="profissional">profissional</option>
                    <option value="premium">premium</option>
                </select>

                <button>Criar</button>
            </form>

            <div class="mensagem">{mensagem}</div>

            <table>
                <tr>
                    <th>Usuário</th>
                    <th>Cargo</th>
                    <th>Email</th>
                    <th>Empresa</th>
                    <th>Plano</th>
                    <th>Status</th>
                    <th>Pagamento</th>
                    <th>Ações</th>
                </tr>
                {tabela}
            </table>
        </div>
        """)

    finally:
        if conn:
            devolver_conexao(conn)


# ================= LIBERAR =================
@usuarios_bp.route("/liberar_usuario/<usuario>", methods=["POST"])
def liberar_usuario(usuario):
    dias = int(request.form.get("dias", 0))
    vencimento = datetime.now() + timedelta(days=dias)

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE pagamentos
        SET status='pago', data=NOW(), vencimento=%s
        WHERE usuario=%s
        """, (vencimento, usuario))

        if cursor.rowcount == 0:
            cursor.execute("""
            INSERT INTO pagamentos (usuario, status, data, vencimento)
            VALUES (%s, 'pago', NOW(), %s)
            """, (usuario, vencimento))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Erro liberar:", e)

    finally:
        devolver_conexao(conn)

    return redirect("/usuarios")


# ================= BLOQUEAR =================
@usuarios_bp.route("/bloquear_usuario/<usuario>", methods=["POST"])
def bloquear_usuario(usuario):
    dias = int(request.form.get("dias", 0))
    vencimento = datetime.now() + timedelta(days=dias)

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE pagamentos
        SET status='bloqueado', vencimento=%s
        WHERE usuario=%s
        """, (vencimento, usuario))

        if cursor.rowcount == 0:
            cursor.execute("""
            INSERT INTO pagamentos (usuario, status, data, vencimento)
            VALUES (%s, 'bloqueado', NOW(), %s)
            """, (usuario, vencimento))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Erro bloquear:", e)

    finally:
        devolver_conexao(conn)

    return redirect("/usuarios")
    # ================= EDITAR USUARIO =================
@usuarios_bp.route("/editar_usuario/<usuario>", methods=["GET", "POST"])
def editar_usuario(usuario):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        novo_cargo = request.form.get("cargo")
        cursor.execute("""
        UPDATE usuarios SET cargo=%s WHERE usuario=%s
        """, (novo_cargo, usuario))
        conn.commit()

    cursor.execute("SELECT cargo FROM usuarios WHERE usuario=%s", (usuario,))
    cargo = cursor.fetchone()[0]

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
        <h2>Editar Usuário: {usuario}</h2>

        <form method="POST">
            <select name="cargo">
                <option value="operador" {"selected" if cargo=="operador" else ""}>operador</option>
                <option value="admin" {"selected" if cargo=="admin" else ""}>admin</option>
            </select>
            <button>Salvar</button>
        </form>
    </div>
    """)


# ================= ALTERAR SENHA =================
@usuarios_bp.route("/alterar_senha/<usuario>", methods=["GET", "POST"])
def alterar_senha(usuario):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    if request.method == "POST":
        nova = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE usuarios SET senha=%s WHERE usuario=%s
        """, (generate_password_hash(nova), usuario))

        conn.commit()
        devolver_conexao(conn)

        return redirect("/usuarios")

    return container(f"""
    <div class="card">
        <h2>Nova senha para {usuario}</h2>

        <form method="POST">
            <input name="senha" placeholder="Nova senha" required>
            <button>Alterar</button>
        </form>
    </div>
    """)


# ================= MUDAR PLANO =================
@usuarios_bp.route("/mudar_plano/<usuario>", methods=["GET", "POST"])
def mudar_plano(usuario):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    if request.method == "POST":
        plano = request.form.get("plano")

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE usuarios SET plano=%s WHERE usuario=%s
        """, (plano, usuario))

        conn.commit()
        devolver_conexao(conn)

        return redirect("/usuarios")

    return container(f"""
    <div class="card">
        <h2>Plano de {usuario}</h2>

        <form method="POST">
            <select name="plano">
                <option value="basico">basico</option>
                <option value="profissional">profissional</option>
                <option value="premium">premium</option>
            </select>
            <button>Salvar</button>
        </form>
    </div>
    """)


# ================= EXCLUIR =================
@usuarios_bp.route("/excluir_usuario/<usuario>")
def excluir_usuario(usuario):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario,))
    cursor.execute("DELETE FROM pagamentos WHERE usuario=%s", (usuario,))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")



   
