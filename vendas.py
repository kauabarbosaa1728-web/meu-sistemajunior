from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao, registrar_log
from layout import container

vendas_bp = Blueprint("vendas_bp", __name__)

# ================= VENDAS =================
@vendas_bp.route("/vendas", methods=["GET", "POST"])
def vendas():

    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()
    msg = ""

    # ================= REALIZAR VENDA =================
    if request.method == "POST":
        produto_id = request.form.get("produto_id")
        qtd = request.form.get("qtd")

        try:
            qtd = int(qtd)

            # 🔥 BUSCAR PRODUTO
            cursor.execute("SELECT produto, quantidade, valor FROM estoque WHERE id=%s", (produto_id,))
            produto = cursor.fetchone()

            if not produto:
                msg = "❌ Produto não encontrado"
            else:
                nome, estoque_qtd, valor = produto

                if qtd > estoque_qtd:
                    msg = "❌ Estoque insuficiente"
                else:
                    total = qtd * float(valor or 0)

                    # 🔥 BAIXAR ESTOQUE
                    cursor.execute("""
                    UPDATE estoque
                    SET quantidade = quantidade - %s
                    WHERE id=%s
                    """, (qtd, produto_id))

                    # 🔥 REGISTRAR VENDA
                    cursor.execute("""
                    INSERT INTO vendas (produto, quantidade, valor_total, usuario)
                    VALUES (%s, %s, %s, %s)
                    """, (nome, qtd, total, session["user"]))

                    # 🔥 REGISTRAR FINANCEIRO (ENTRADA)
                    cursor.execute("""
                    INSERT INTO financeiro (tipo, valor, descricao, usuario)
                    VALUES ('entrada', %s, %s, %s)
                    """, (total, f"Venda de {nome}", session["user"]))

                    conn.commit()

                    registrar_log(session["user"], "venda", nome)

                    msg = "✅ Venda realizada com sucesso!"

        except Exception as e:
            conn.rollback()
            msg = f"❌ Erro: {e}"

    # ================= LISTAR PRODUTOS =================
    cursor.execute("SELECT id, produto, quantidade FROM estoque ORDER BY produto")
    produtos = cursor.fetchall()

    opcoes = ""
    for p in produtos:
        opcoes += f"<option value='{p[0]}'>{p[1]} (Estoque: {p[2]})</option>"

    # ================= HISTÓRICO =================
    cursor.execute("""
    SELECT produto, quantidade, valor_total, data
    FROM vendas
    WHERE usuario=%s
    ORDER BY id DESC
    """, (session["user"],))
    vendas = cursor.fetchall()

    tabela = ""
    for v in vendas:
        tabela += f"""
        <tr>
        <td>{v[0]}</td>
        <td>{v[1]}</td>
        <td>R$ {float(v[2]):.2f}</td>
        <td>{v[3]}</td>
        </tr>
        """

    devolver_conexao(conn)

    return container(f"""
    <div class="card">
    <h2>🛒 VENDAS</h2>

    <form method="POST" style="display:flex; flex-direction:column; gap:10px; max-width:300px;">
        <select name="produto_id">
            {opcoes}
        </select>

        <input name="qtd" placeholder="Quantidade">
        <button>Vender</button>
    </form>

    <p>{msg}</p>

    <hr>

    <h3>📋 Histórico de vendas</h3>

    <table>
    <tr>
    <th>Produto</th><th>Qtd</th><th>Total</th><th>Data</th>
    </tr>
    {tabela}
    </table>

    </div>
    """)
