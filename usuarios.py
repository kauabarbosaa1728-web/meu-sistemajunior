from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash
from banco import conectar, devolver_conexao, registrar_log, permissoes_por_plano
from layout import container, acesso_negado

usuarios_bp = Blueprint("usuarios_bp", __name__)

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

                if cargo == "admin":
                    ativo = 1
                    pode_estoque = 1
                    pode_transferencia = 1
                    pode_historico = 1
                    pode_usuarios = 1
                    pode_editar_estoque = 1
                    pode_excluir_estoque = 1
                    pode_logs = 1
                    plano = "admin"
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
                    usuario, senha, cargo, ativo, email, plano, nome_empresa,
                    pode_estoque, pode_transferencia, pode_historico,
                    pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    user,
                    generate_password_hash(senha),
                    cargo,
                    ativo,
                    email,
                    plano,
                    nome_empresa,
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
                registrar_log(session["user"], "criar_usuario", f"Usuário criado: {user} | Cargo: {cargo} | Plano: {plano}")
            except:
                conn.rollback()
                mensagem = "Não foi possível criar o usuário. Talvez ele já exista."

        # 🔥 BUSCAR USUÁRIOS
        cursor.execute("""
        SELECT usuario, cargo, online, ativo, email, plano, nome_empresa,
               pode_estoque, pode_transferencia, pode_historico,
               pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
        FROM usuarios
        ORDER BY usuario
        """)
        dados = cursor.fetchall()

        # 🔥 BUSCAR STATUS DE PAGAMENTO
        cursor.execute("SELECT usuario, status FROM pagamentos")
        pagamentos = dict(cursor.fetchall())

        tabela = ""
        for u, c, o, ativo, email, plano, nome_empresa, pe, pt, ph, pu, ped, pex, pl in dados:
            status_online = "🟢 Online" if o else "🔴 Offline"
            status_ativo = "✅ Ativo" if ativo else "⛔ Inativo"

            status_pagamento = pagamentos.get(u, "bloqueado")
            cor = "#00ff00" if status_pagamento == "pago" else "red"
            texto_status = "PAGO" if status_pagamento == "pago" else "BLOQUEADO"

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
                acoes += f'<a href="/mudar_plano/{u}" class="btn-edit">Mudar plano</a>'
                acoes += f'<a href="/excluir_usuario/{u}" class="btn-danger" onclick="return confirm(\'Deseja excluir este usuário?\')">Excluir</a>'

                # 🔥 BOTÕES NOVOS
                acoes += f'''
                <br><br>
                <a href="/liberar_usuario/{u}" style="
                background:#00ff00;
                padding:5px 10px;
                color:#000;
                border-radius:5px;
                text-decoration:none;
                font-weight:bold;
                ">💸 Liberar</a>

                <a href="/bloquear_usuario/{u}" style="
                background:red;
                padding:5px 10px;
                color:#fff;
                border-radius:5px;
                text-decoration:none;
                margin-left:5px;
                font-weight:bold;
                ">🔒 Bloquear</a>
                '''
            else:
                acoes = "Protegido"

            tabela += f"""
            <tr>
                <td>{u}</td>
                <td>{c}</td>
                <td>{email or '-'}</td>
                <td>{nome_empresa or '-'}</td>
                <td>{plano or '-'}</td>
                <td>{status_online}<br>{status_ativo}</td>
                <td style="color:{cor};font-weight:bold;">{texto_status}</td>
                <td>{texto_permissoes}</td>
                <td>{acoes}</td>
            </tr>
            """

        return container(f"""
        <div class="card">
            <h2>👤 USUÁRIOS</h2>

            <p>{mensagem}</p>

            <table>
                <tr>
                    <th>Usuário</th>
                    <th>Cargo</th>
                    <th>Email</th>
                    <th>Empresa</th>
                    <th>Plano</th>
                    <th>Status</th>
                    <th>Pagamento</th>
                    <th>Permissões</th>
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
    if session.get("cargo") != "admin":
        return acesso_negado()

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
    if session.get("cargo") != "admin":
        return acesso_negado()

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
                    <th>E-mail</th>
                    <th>Empresa</th>
                    <th>Plano</th>
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
        devolver_conexao(conn)

@usuarios_bp.route("/editar_usuario/<usuario_alvo>", methods=["GET", "POST"])
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
        devolver_conexao(conn)

@usuarios_bp.route("/alterar_senha/<usuario_alvo>", methods=["GET", "POST"])
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
        devolver_conexao(conn)

@usuarios_bp.route("/mudar_plano/<usuario_alvo>", methods=["GET", "POST"])
def mudar_plano(usuario_alvo):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    if usuario_alvo == "admin":
        return container("""
        <div class="card">
            <h2 class="erro">⛔ O plano do admin não pode ser alterado aqui.</h2>
            <p><a href="/usuarios">⬅ Voltar</a></p>
        </div>
        """)

    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        mensagem = ""

        cursor.execute("""
        SELECT usuario, plano
        FROM usuarios
        WHERE usuario=%s
        """, (usuario_alvo,))
        dado = cursor.fetchone()

        if not dado:
            return container("<div class='card'><h2>Usuário não encontrado.</h2></div>")

        usuario_nome, plano_atual = dado

        if request.method == "POST":
            novo_plano = request.form["plano"].strip().lower()
            permissoes = permissoes_por_plano(novo_plano)

            cursor.execute("""
            UPDATE usuarios
            SET plano=%s,
                pode_estoque=%s,
                pode_transferencia=%s,
                pode_historico=%s,
                pode_usuarios=%s,
                pode_editar_estoque=%s,
                pode_excluir_estoque=%s,
                pode_logs=%s
            WHERE usuario=%s
            """, (
                novo_plano,
                permissoes["pode_estoque"],
                permissoes["pode_transferencia"],
                permissoes["pode_historico"],
                permissoes["pode_usuarios"],
                permissoes["pode_editar_estoque"],
                permissoes["pode_excluir_estoque"],
                permissoes["pode_logs"],
                usuario_alvo
            ))
            conn.commit()

            registrar_log(session["user"], "mudar_plano", f"Usuário: {usuario_alvo} | Plano: {plano_atual} -> {novo_plano}")
            mensagem = "Plano alterado com sucesso."
            plano_atual = novo_plano

        selected_basico = "selected" if plano_atual == "basico" else ""
        selected_profissional = "selected" if plano_atual == "profissional" else ""
        selected_premium = "selected" if plano_atual == "premium" else ""

        return container(f"""
        <div class="card">
            <h2>💳 MUDAR PLANO</h2>
            <p>Usuário: <b>{usuario_nome}</b></p>
            <p>Plano atual: <b>{plano_atual}</b></p>

            <form method="POST">
                <select name="plano" required>
                    <option value="basico" {selected_basico}>basico - R$ 39,90/mês</option>
                    <option value="profissional" {selected_profissional}>profissional - R$ 79,90/mês</option>
                    <option value="premium" {selected_premium}>premium - R$ 129,90/mês</option>
                </select>

                <button>Salvar plano</button>
            </form>

            <div class="mensagem">{mensagem}</div>
            <p><a href="/usuarios">⬅ Voltar</a></p>
        </div>
        """)
    except Exception as e:
        return container(f'<div class="card"><h2 class="erro">Erro ao mudar plano: {e}</h2></div>')
    finally:
        devolver_conexao(conn)

@usuarios_bp.route("/excluir_usuario/<usuario_alvo>")
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
        devolver_conexao(conn)
