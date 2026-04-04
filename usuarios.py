from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash
from banco import conectar, devolver_conexao
from layout import container, acesso_negado
from datetime import datetime, timedelta

usuarios_bp = Blueprint("usuarios_bp", __name__)

# ================= USUÁRIOS =================
@usuarios_bp.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()
    mensagem = ""

    # ================= CRIAR =================
    if request.method == "POST":
        try:
            user = request.form["user"].strip()
            senha = request.form["senha"].strip()
            cargo = request.form["cargo"].strip()
            email = request.form.get("email", "").strip()
            nome_empresa = request.form.get("nome_empresa", "").strip()
            plano = request.form.get("plano", "basico").strip().lower()

            cursor.execute("""
            INSERT INTO usuarios (usuario, senha, cargo, ativo, email, plano, nome_empresa)
            VALUES (%s,%s,%s,1,%s,%s,%s)
            """, (user, generate_password_hash(senha), cargo, email, plano, nome_empresa))

            conn.commit()
            mensagem = "Usuário criado com sucesso."
        except Exception as e:
            conn.rollback()
            mensagem = f"Erro ao criar usuário: {e}"

    # ================= LISTAGEM =================
    cursor.execute("""
    SELECT usuario, cargo, online, ativo, email, plano, nome_empresa
    FROM usuarios ORDER BY usuario
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
            acoes = f"""
            <form action="/usuarios/editar_usuario/{u}" method="GET" style="display:inline;">
                <button>Editar</button>
            </form>

            <form action="/usuarios/alterar_senha/{u}" method="POST" style="display:inline;">
                <input type="password" name="senha" placeholder="Nova senha" required style="width:120px;">
                <button>Senha</button>
            </form>

            <form action="/usuarios/mudar_plano/{u}" method="POST" style="display:inline;">
                <select name="plano">
                    <option value="basico">basico</option>
                    <option value="profissional">profissional</option>
                    <option value="premium">premium</option>
                </select>
                <button>Plano</button>
            </form>

            <form action="/usuarios/excluir_usuario/{u}" method="POST" style="display:inline;">
                <button style="color:red;">Excluir</button>
            </form>

            <br><br>

            <form action="/usuarios/liberar_usuario/{u}" method="POST" style="display:inline;">
                <input type="number" name="dias" placeholder="Dias" required style="width:60px;">
                <button style="background:#00ff00;color:#000;">💸 Liberar</button>
            </form>

            <form action="/usuarios/bloquear_usuario/{u}" method="POST" style="display:inline;">
                <input type="number" name="dias" placeholder="Dias" required style="width:60px;">
                <button style="background:red;color:#fff;">🔒 Bloquear</button>
            </form>
            """
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

    devolver_conexao(conn)

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


# ================= EDITAR =================
@usuarios_bp.route("/editar_usuario/<usuario>")
def editar_usuario(usuario):
    return redirect("/usuarios")


# ================= ALTERAR SENHA =================
@usuarios_bp.route("/alterar_senha/<usuario>", methods=["POST"])
def alterar_senha(usuario):
    nova = request.form.get("senha")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios SET senha=%s WHERE usuario=%s
    """, (generate_password_hash(nova), usuario))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")


# ================= MUDAR PLANO =================
@usuarios_bp.route("/mudar_plano/<usuario>", methods=["POST"])
def mudar_plano(usuario):
    novo_plano = request.form.get("plano")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios SET plano=%s WHERE usuario=%s
    """, (novo_plano, usuario))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")


# ================= LIBERAR =================
@usuarios_bp.route("/liberar_usuario/<usuario>", methods=["POST"])
def liberar_usuario(usuario):
    dias = int(request.form.get("dias", 0))
    vencimento = datetime.now() + timedelta(days=dias)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pagamentos (usuario, status, data, vencimento)
    VALUES (%s, 'pago', NOW(), %s)
    ON CONFLICT (usuario)
    DO UPDATE SET status='pago', vencimento=%s
    """, (usuario, vencimento, vencimento))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")


# ================= BLOQUEAR =================
@usuarios_bp.route("/bloquear_usuario/<usuario>", methods=["POST"])
def bloquear_usuario(usuario):
    dias = int(request.form.get("dias", 0))
    vencimento = datetime.now() + timedelta(days=dias)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pagamentos (usuario, status, data, vencimento)
    VALUES (%s, 'bloqueado', NOW(), %s)
    ON CONFLICT (usuario)
    DO UPDATE SET status='bloqueado', vencimento=%s
    """, (usuario, vencimento, vencimento))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")


# ================= EXCLUIR =================
@usuarios_bp.route("/excluir_usuario/<usuario>", methods=["POST"])
def excluir_usuario(usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario,))
    cursor.execute("DELETE FROM pagamentos WHERE usuario=%s", (usuario,))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")

# ================= FALLBACK ROTAS (ANTI-404) =================

@usuarios_bp.route("/usuarios/editar_usuario/<usuario>")
def editar_usuario_fallback(usuario):
    return redirect("/usuarios")


@usuarios_bp.route("/usuarios/alterar_senha/<usuario>", methods=["POST"])
def alterar_senha_fallback(usuario):
    nova = request.form.get("senha")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios SET senha=%s WHERE usuario=%s
    """, (generate_password_hash(nova), usuario))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")


@usuarios_bp.route("/usuarios/mudar_plano/<usuario>", methods=["POST"])
def mudar_plano_fallback(usuario):
    novo_plano = request.form.get("plano")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios SET plano=%s WHERE usuario=%s
    """, (novo_plano, usuario))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")

@usuarios_bp.route("/usuarios/excluir_usuario/<usuario>", methods=["POST"])
def excluir_usuario_fallback(usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario,))
    cursor.execute("DELETE FROM pagamentos WHERE usuario=%s", (usuario,))

    conn.commit()
    devolver_conexao(conn)

    return redirect("/usuarios")
    # ================= LIBERAR USUARIO =================
@usuarios_bp.route("/usuarios/liberar_usuario/<usuario_alvo>")
def liberar_usuario(usuario_alvo):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE usuarios
        SET ativo = TRUE
        WHERE usuario = %s
        """, (usuario_alvo,))

        conn.commit()

    except Exception as e:
        print("Erro ao liberar:", e)

    finally:
        cursor.close()
        devolver_conexao(conn)

    return redirect("/usuarios")
    # ================= BLOQUEAR USUARIO =================
@usuarios_bp.route("/usuarios/bloquear_usuario/<usuario_alvo>")
def bloquear_usuario(usuario_alvo):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE usuarios
        SET ativo = FALSE
        WHERE usuario = %s
        """, (usuario_alvo,))

        conn.commit()

    except Exception as e:
        print("Erro ao bloquear:", e)

    finally:
        cursor.close()
        devolver_conexao(conn)

    return redirect("/usuarios")
