from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash
from banco import conectar, devolver_conexao, registrar_log
from layout import container, acesso_negado
from datetime import datetime, timedelta

usuarios_bp = Blueprint("usuarios_bp", __name__)

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

            pode_estoque = 1 if request.form.get("pode_estoque") else 0
            pode_transferencia = 1 if request.form.get("pode_transferencia") else 0
            pode_historico = 1 if request.form.get("pode_historico") else 0
            pode_usuarios = 1 if request.form.get("pode_usuarios") else 0
            pode_logs = 1 if request.form.get("pode_logs") else 0
            pode_editar_estoque = 1 if request.form.get("pode_editar_estoque") else 0
            pode_excluir_estoque = 1 if request.form.get("pode_excluir_estoque") else 0

            cursor.execute("""
            INSERT INTO usuarios (
                usuario, senha, cargo, ativo, email, plano, nome_empresa,
                pode_estoque, pode_transferencia, pode_historico,
                pode_usuarios, pode_logs, pode_editar_estoque, pode_excluir_estoque
            )
            VALUES (%s,%s,%s,0,%s,%s,%s,
                    %s,%s,%s,
                    %s,%s,%s,%s)
            """, (
                user,
                generate_password_hash(senha),
                cargo,
                email,
                plano,
                nome_empresa,
                pode_estoque,
                pode_transferencia,
                pode_historico,
                pode_usuarios,
                pode_logs,
                pode_editar_estoque,
                pode_excluir_estoque
            ))

            conn.commit()
            mensagem = "✅ Usuário criado com sucesso"

        except Exception as e:
            conn.rollback()
            mensagem = f"❌ Erro: {e}"

    # ================= LISTAR =================
    cursor.execute("""
    SELECT usuario, cargo, online, ativo, email, plano, nome_empresa
    FROM usuarios ORDER BY usuario
    """)
    dados = cursor.fetchall()

    tabela = ""

    for u, c, o, ativo, email, plano, nome_empresa in dados:

        status = f"<span class='badge on'>Online</span>" if o else f"<span class='badge off'>Offline</span>"

        if u != "admin":
            acoes = f"""
            <div class="acoes">

                <form action="/usuarios/alterar_senha/{u}" method="POST">
                    <input type="password" name="senha" placeholder="Senha">
                    <button class="btn small">Salvar</button>
                </form>

                <form action="/usuarios/mudar_plano/{u}" method="POST">
                    <select name="plano">
                        <option value="basico">Básico</option>
                        <option value="profissional">Profissional</option>
                        <option value="premium">Premium</option>
                    </select>
                    <button class="btn small">OK</button>
                </form>

                <form action="/usuarios/excluir_usuario/{u}" method="POST">
                    <button class="btn danger small">Excluir</button>
                </form>

            </div>
            """
        else:
            acoes = "<span class='protegido'>Protegido</span>"

        tabela += f"""
        <tr>
            <td>{u}</td>
            <td>{c}</td>
            <td>{email or '-'}</td>
            <td>{nome_empresa or '-'}</td>
            <td>{plano}</td>
            <td>{status}</td>
            <td>{acoes}</td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""

    <div class="wrap">

        <h2 class="title">👤 Usuários</h2>

        <div class="box">
            <h3>Criar usuário</h3>

            <form method="POST" class="form-grid">
                <input name="user" placeholder="Usuário" required>
                <input name="senha" placeholder="Senha" required>
                <input name="email" placeholder="E-mail">
                <input name="nome_empresa" placeholder="Empresa">

                <select name="cargo">
                    <option value="operador">Operador</option>
                    <option value="admin">Admin</option>
                </select>

                <select name="plano">
                    <option value="basico">Básico</option>
                    <option value="profissional">Profissional</option>
                    <option value="premium">Premium</option>
                </select>

                <div class="permissoes">
                    <label><input type="checkbox" name="pode_estoque"> Estoque</label>
                    <label><input type="checkbox" name="pode_transferencia"> Transferência</label>
                    <label><input type="checkbox" name="pode_historico"> Histórico</label>
                    <label><input type="checkbox" name="pode_usuarios"> Usuários</label>
                    <label><input type="checkbox" name="pode_logs"> Logs</label>
                    <label><input type="checkbox" name="pode_editar_estoque"> Editar</label>
                    <label><input type="checkbox" name="pode_excluir_estoque"> Excluir</label>
                </div>

                <button class="btn primary full">Criar</button>
            </form>

            <p class="msg">{mensagem}</p>
        </div>

        <div class="box">
            <h3>Lista de usuários</h3>

            <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Usuário</th>
                        <th>Cargo</th>
                        <th>Email</th>
                        <th>Empresa</th>
                        <th>Plano</th>
                        <th>Status</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {tabela}
                </tbody>
            </table>
            </div>
        </div>

    </div>

    <style>

    .wrap {{ max-width:1200px; margin:auto; }}

    .box {{
        background:#0b0b0b;
        border:1px solid #2c2c2c;
        padding:20px;
        border-radius:12px;
        margin-bottom:20px;
    }}

    .form-grid {{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
    }}

    input, select {{
        padding:10px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    .permissoes {{
        grid-column:span 3;
        display:flex;
        flex-wrap:wrap;
        gap:10px;
    }}

    .btn {{
        padding:8px 10px;
        border:none;
        border-radius:6px;
        cursor:pointer;
    }}

    .small {{ font-size:12px; padding:5px; }}

    .primary {{ background:#3b82f6; color:white; }}
    .danger {{ background:#ef4444; color:white; }}

    .full {{ grid-column:span 3; }}

    .msg {{ color:#22c55e; }}

    table {{ width:100%; border-collapse:collapse; }}
    th {{ background:#111; padding:10px; }}
    td {{ padding:10px; border-top:1px solid #222; }}

    .acoes {{ display:flex; gap:5px; flex-wrap:wrap; }}

    .badge {{
        padding:4px 8px;
        border-radius:6px;
        font-size:12px;
        font-weight:bold;
    }}

    .on {{ background:#22c55e; color:black; }}
    .off {{ background:#ef4444; color:white; }}

    .protegido {{ color:#888; }}

    </style>
    """)
