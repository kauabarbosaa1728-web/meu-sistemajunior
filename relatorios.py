from flask import Blueprint, session, redirect
from banco import conectar, devolver_conexao
from layout import container

relatorios_bp = Blueprint("relatorios_bp", __name__)


# ================= HISTÓRICO DE ESTOQUE =================
@relatorios_bp.route("/historico_estoque")
def historico_estoque():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    if conn is None:
        return container("<div class='card'>Erro ao conectar com banco</div>")

    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT produto, quantidade, categoria, valor
        FROM estoque
        ORDER BY id DESC
        """)
        dados = cursor.fetchall()

        linhas = ""
        total_qtd = 0
        total_valor = 0

        for produto, qtd, categoria, valor in dados:
            valor = valor or 0
            total = qtd * valor

            total_qtd += qtd
            total_valor += total

            linhas += f"""
            <tr>
                <td>{produto}</td>
                <td>{qtd}</td>
                <td>{categoria or '-'}</td>
                <td>R$ {valor:.2f}</td>
                <td>R$ {total:.2f}</td>
            </tr>
            """

        html = f"""
        <div class="card">
            <h2>📦 Relatório de Estoque</h2>

            <input type="text" id="busca" placeholder="Buscar produto..." onkeyup="filtrar()">

            <div style="margin-top:15px;">
                <b>Total de Itens:</b> {total_qtd} |
                <b>Valor Total:</b> R$ {total_valor:.2f}
            </div>
        </div>

        <div class="card">
            <table id="tabela" style="width:100%; border-collapse: collapse;">
                <thead>
                    <tr style="background:#111827;">
                        <th>Produto</th>
                        <th>Qtd</th>
                        <th>Categoria</th>
                        <th>Valor Unitário</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas}
                </tbody>
            </table>
        </div>

        <script>
        function filtrar() {{
            let input = document.getElementById("busca").value.toLowerCase();
            let linhas = document.querySelectorAll("#tabela tbody tr");

            linhas.forEach(tr => {{
                let texto = tr.innerText.toLowerCase();
                tr.style.display = texto.includes(input) ? "" : "none";
            }});
        }}
        </script>
        """

        return container(html)

    except Exception as e:
        return container(f"<div class='card'>Erro: {e}</div>")

    finally:
        devolver_conexao(conn)
