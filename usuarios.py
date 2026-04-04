from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash
from banco import conectar, devolver_conexao, registrar_log, permissoes_por_plano
from layout import container, acesso_negado

usuarios_bp = Blueprint("usuarios_bp", __name__)

# ================= USUÁRIOS =================
@usuarios_bp.route("/usuarios", methods=["GET", "POST"])
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

            acoes = ""
            if u != "admin":
                acoes += f'<a href="/editar_usuario/{u}">Editar</a> | '
                acoes += f'<a href="/alterar_senha/{u}">Senha</a> | '
                acoes += f'<a href="/mudar_plano/{u}">Plano</a> | '
                acoes += f'<a href="/excluir_usuario/{u}">Excluir</a><br><br>'

                # 🔥 AQUI ESTÁ O FIX
                acoes += f'''
                <a href="/usuarios/liberar_usuario/{u}" style="background:#00ff00;color:#000;padding:5px;">💸 Liberar</a>
                <a href="/usuarios/bloquear_usuario/{u}" style="background:red;color:#fff;padding:5px;">🔒 Bloquear</a>
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
@usuarios_bp.route("/liberar_usuario/<usuario>")
def liberar_usuario(usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pagamentos (usuario, status, data)
    VALUES (%s, 'pago', NOW())
    ON CONFLICT (usuario) DO UPDATE
    SET status='pago', data=NOW()
    """, (usuario,))

    conn.commit()
    devolver_conexao(conn)
    return redirect("/usuarios")


# ================= BLOQUEAR =================
@usuarios_bp.route("/bloquear_usuario/<usuario>")
def bloquear_usuario(usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE pagamentos
    SET status='bloqueado'
    WHERE usuario=%s
    """, (usuario,))

    conn.commit()
    devolver_conexao(conn)
    return redirect("/usuarios")
