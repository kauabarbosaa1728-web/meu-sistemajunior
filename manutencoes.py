from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import layout
from datetime import datetime

manutencoes_bp = Blueprint("manutencoes_bp", __name__)

@manutencoes_bp.route("/manutencoes", methods=["GET", "POST"])
def manutencoes_page():

    # 🔒 PROTEÇÃO
    if "user" not in session:
        return redirect("/")

    empresa_id = session.get("empresa_id")

    conn = conectar()
    cursor = conn.cursor()

    # 🔥 CADASTRAR
    if request.method == "POST":
        data = request.form.get("data")
        valor = request.form.get("valor")
        veiculo_id = request.form.get("veiculo_id")
        oficina = request.form.get("oficina")
        descricao = request.form.get("descricao")
        quantidade = request.form.get("quantidade")
        validade = request.form.get("validade")

        cursor.execute("""
        INSERT INTO manutencoes 
        (data, valor, veiculo_id, oficina, descricao, quantidade, validade, empresa_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (data, valor, veiculo_id, oficina, descricao, quantidade, validade, empresa_id))

        conn.commit()
        return redirect("/manutencoes")

    # 🔥 PEGAR VEÍCULOS (ISOLADO)
    cursor.execute("""
    SELECT id, placa 
    FROM veiculos 
    WHERE empresa_id=%s
    """, (empresa_id,))
    veiculos = cursor.fetchall()

    opcoes = ""
    for v in veiculos:
        opcoes += f"<option value='{v[0]}'>{v[1]}</option>"

    # 🔥 LISTAR MANUTENÇÕES (ISOLADO)
    cursor.execute("""
    SELECT m.data, m.valor, v.placa, m.oficina, m.descricao, m.quantidade, m.validade
    FROM manutencoes m
    JOIN veiculos v ON m.veiculo_id = v.id
    WHERE m.empresa_id=%s
    ORDER BY m.id DESC
    """, (empresa_id,))

    dados = cursor.fetchall()

    tabela = ""
    hoje = datetime.now().date()

    for d in dados:
        validade = d[6]

        cor = "#22c55e"
        status = "OK"

        if validade:
            dias = (validade - hoje).days

            if dias < 0:
                cor = "#ef4444"
                status = "VENCIDO"
            elif dias <= 7:
                cor = "#facc15"
                status = "PRÓXIMO"

        tabela += f"""
        <tr>
            <td>{d[0]}</td>
            <td>R$ {d[1]}</td>
            <td>{d[2]}</td>
            <td>{d[3]}</td>
            <td>{d[4]}</td>
            <td>{d[5]}</td>
            <td>{d[6]}</td>
            <td style="color:{cor}; font-weight:bold;">{status}</td>
        </tr>
        """

    cursor.close()
    devolver_conexao(conn)

    return layout(f"""
        <h2>🔧 Manutenções</h2>

        <form method="POST">
            <input type="date" name="data" required>
            <input type="number" step="0.01" name="valor" placeholder="Valor" required>

            <select name="veiculo_id">
                {opcoes}
            </select>

            <input name="oficina" placeholder="Oficina">
            <input name="descricao" placeholder="Descrição">
            <input type="number" name="quantidade" placeholder="Qtd">
            <input type="date" name="validade">

            <button>Salvar</button>
        </form>

        <h3>📋 Histórico:</h3>

        <table>
            <tr>
                <th>Data</th>
                <th>Valor</th>
                <th>Veículo</th>
                <th>Oficina</th>
                <th>Descrição</th>
                <th>Qtd</th>
                <th>Validade</th>
                <th>Status</th>
            </tr>
            {tabela}
        </table>
    """)
