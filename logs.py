from flask import Blueprint, session, redirect
from banco import conectar
from layout import container, acesso_negado, tem_permissao

logs_bp = Blueprint("logs_bp", __name__)

@logs_bp.route("/logs")
def logs():
    if "user" not in session:
        return redirect("/")

    if not tem_permissao("pode_logs"):
        return acesso_negado()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT usuario, acao, detalhes, data
        FROM logs
        ORDER BY data DESC
        LIMIT 100
    """)

    dados = cursor.fetchall()

    html = """
    <div class="card">
        <h2>📜 Logs do Sistema</h2>
        <table>
            <tr>
                <th>Usuário</th>
                <th>Ação</th>
                <th>Detalhes</th>
                <th>Data</th>
            </tr>
    """

    for u, a, d, dt in dados:
        html += f"""
        <tr>
            <td>{u}</td>
            <td>{a}</td>
            <td>{d}</td>
            <td>{dt}</td>
        </tr>
        """

    html += "</table></div>"

    return container(html)
