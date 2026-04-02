from datetime import datetime

tabela = ""

for u, c, o, ativo, email, plano, nome_empresa, pe, pt, ph, pu, ped, pex, pl, validade in dados:

    status_online = "🟢 Online" if o else "🔴 Offline"
    status_ativo = "✅ Ativo" if ativo else "⛔ Inativo"

    status_pagamento = "❌ VENCIDO"
    dias_restantes = 0
    cor = "red"

    if validade:
        diff = (validade - datetime.now()).days
        if diff >= 0:
            status_pagamento = "✅ ATIVO"
            dias_restantes = diff
            cor = "#00ff00"

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
        acoes += f'<br><a href="/liberar/{u}/5">🔥 5d</a>'
        acoes += f' | <a href="/liberar/{u}/10">⚡ 10d</a>'
        acoes += f' | <a href="/liberar/{u}/30">💎 30d</a>'
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
        <td style="color:{cor}">
            {status_pagamento}<br>
            {dias_restantes} dias
        </td>
        <td>{texto_permissoes}</td>
        <td>{acoes}</td>
    </tr>
    """

# 🔥 AQUI TERMINA O FOR

html = f"""
<div class="card">
    <h2>👤 USUÁRIOS</h2>

    <form method="POST">
        <input name="user" placeholder="Usuário" required>
        <input name="senha" placeholder="Senha" required>
        <input name="email" placeholder="E-mail">
        <input name="nome_empresa" placeholder="Empresa">

        <select name="cargo" required>
            <option value="operador">operador</option>
            <option value="admin">admin</option>
        </select>

        <select name="plano">
            <option value="basico">basico</option>
            <option value="profissional">profissional</option>
            <option value="premium">premium</option>
        </select>

        <div class="permissoes-box">
            <label><input type="checkbox" name="ativo" value="1" checked> Usuário ativo</label>
            <label><input type="checkbox" name="pode_estoque" value="1"> Estoque</label>
            <label><input type="checkbox" name="pode_transferencia" value="1"> Transferência</label>
            <label><input type="checkbox" name="pode_historico" value="1"> Histórico</label>
            <label><input type="checkbox" name="pode_usuarios" value="1"> Usuários</label>
            <label><input type="checkbox" name="pode_editar_estoque" value="1"> Editar estoque</label>
            <label><input type="checkbox" name="pode_excluir_estoque" value="1"> Excluir estoque</label>
            <label><input type="checkbox" name="pode_logs" value="1"> Logs</label>
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
"""

return container(html)

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
                    <th>Pagamento</th>
                    <th>Permissões</th>
                    <th>Ações</th>
                </tr>
                {tabela}
            </table>
        </div>
        """)

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
                    <label><input type="checkbox" name="ativo" value="1" {checked_ativo}>Usuário ativo</label>
                    <label><input type="checkbox" name="pode_estoque" value="1" {checked_pe}>Estoque</label>
                    <label><input type="checkbox" name="pode_transferencia" value="1" {checked_pt}>Transferência</label>
                    <label><input type="checkbox" name="pode_historico" value="1" {checked_ph}>Histórico</label>
                    <label><input type="checkbox" name="pode_usuarios" value="1" {checked_pu}>Usuários</label>
                    <label><input type="checkbox" name="pode_editar_estoque" value="1" {checked_ped}>Editar</label>
                    <label><input type="checkbox" name="pode_excluir_estoque" value="1" {checked_pex}>Excluir</label>
                    <label><input type="checkbox" name="pode_logs" value="1" {checked_pl}>Logs</label>
                </div>

                <button>Salvar</button>
            </form>

            <p><a href="/usuarios">⬅ Voltar</a></p>
        </div>
        """)
    finally:
        devolver_conexao(conn)


@usuarios_bp.route("/excluir_usuario/<usuario_alvo>")
def excluir_usuario(usuario_alvo):
    if "user" not in session:
        return redirect("/")

    if session.get("cargo") != "admin":
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE usuario=%s", (usuario_alvo,))
    conn.commit()

    devolver_conexao(conn)
    return redirect("/usuarios")
