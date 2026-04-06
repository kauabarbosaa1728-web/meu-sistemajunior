from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash
from banco import conectar, devolver_conexao, registrar_log
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

    # CRIAR USUÁRIO
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
            VALUES (%s,%s,%s,0,%s,%s,%s)
            """, (user, generate_password_hash(senha), cargo, email, plano, nome_empresa))

            conn.commit()
            mensagem = "Usuário criado."

        except Exception as e:
            conn.rollback()
            mensagem = f"Erro ao criar usuário: {e}"

    # LISTAR
    cursor.execute("""
    SELECT usuario, cargo, online, ativo, email, plano, nome_empresa
    FROM usuarios ORDER BY usuario
    """)
    dados = cursor.fetchall()

    tabela = ""

    for u, c, o, ativo, email, plano, nome_empresa in dados:
        status_online = "🟢 Online" if o else "🔴 Offline"

        if u != "admin":
            acoes = f"""
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
                <th>Ações</th>
            </tr>
            {tabela}
        </table>
    </div>
    """)
