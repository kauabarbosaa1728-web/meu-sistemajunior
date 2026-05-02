from flask import Blueprint, request, redirect, session, send_file
from banco import conectar, devolver_conexao
from layout import container
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

manutencoes_bp = Blueprint("manutencoes_bp", __name__)

PDF_FOLDER = "static/pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)


@manutencoes_bp.route("/manutencoes", methods=["GET", "POST"])
def manutencoes_page():

    if "user" not in session:
        return redirect("/")

    empresa_id = session.get("empresa_id")

    conn = conectar()
    cursor = conn.cursor()

    # ================= CADASTRAR =================
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

    # ================= VEÍCULOS =================
    cursor.execute("""
    SELECT id, placa 
    FROM veiculos 
    WHERE empresa_id=%s
    """, (empresa_id,))
    veiculos = cursor.fetchall()

    opcoes = ""
    for v in veiculos:
        opcoes += f"<option value='{v[0]}'>{v[1]}</option>"

    # ================= LISTA =================
    cursor.execute("""
    SELECT m.id, m.data, m.valor, v.placa, m.oficina, m.descricao, m.quantidade, m.validade
    FROM manutencoes m
    JOIN veiculos v ON m.veiculo_id = v.id
    WHERE m.empresa_id=%s
    ORDER BY m.id DESC
    """, (empresa_id,))

    dados = cursor.fetchall()

    tabela = ""
    hoje = datetime.now().date()

    for d in dados:
        validade = d[7]

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
            <td>{d[1]}</td>
            <td>R$ {d[2]}</td>
            <td>{d[3]}</td>
            <td>{d[4]}</td>
            <td>{d[5]}</td>
            <td>{d[6]}</td>
            <td>{d[7]}</td>
            <td style="color:{cor}; font-weight:bold;">{status}</td>
            <td><a href="/gerar-pdf/{d[0]}">📄 PDF</a></td>
        </tr>
        """

    cursor.close()
    devolver_conexao(conn)

    return container(f"""

<style>

.card {{
    background:#0f172a;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
    box-shadow:0 0 10px rgba(0,0,0,0.3);
}}

.form-grid {{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:10px;
}}

input, select {{
    padding:10px;
    border-radius:8px;
    border:none;
    background:#020617;
    color:white;
}}

.btn {{
    margin-top:10px;
    padding:12px;
    width:100%;
    background:#2563eb;
    border:none;
    border-radius:8px;
    color:white;
    font-weight:bold;
    cursor:pointer;
}}

.btn:hover {{
    background:#1d4ed8;
}}

.tabela {{
    width:100%;
    border-collapse:collapse;
}}

.tabela th, .tabela td {{
    padding:10px;
    border-bottom:1px solid #1e293b;
}}

</style>

<h2>🔧 Manutenções</h2>

<div class="card">
<form method="POST">

<div class="form-grid">
<input type="date" name="data" required>
<input type="number" step="0.01" name="valor" placeholder="Valor" required>

<select name="veiculo_id">
{opcoes}
</select>

<input name="oficina" placeholder="Oficina">
<input name="descricao" placeholder="Descrição">
<input type="number" name="quantidade" placeholder="Qtd">
<input type="date" name="validade">
</div>

<button class="btn">💾 Salvar</button>

</form>
</div>

<h3>📋 Histórico</h3>

<div class="card">
<table class="tabela">
<tr>
<th>Data</th>
<th>Valor</th>
<th>Veículo</th>
<th>Oficina</th>
<th>Descrição</th>
<th>Qtd</th>
<th>Validade</th>
<th>Status</th>
<th>PDF</th>
</tr>
{tabela}
</table>
</div>

""")


# ================= GERAR PDF =================
@manutencoes_bp.route("/gerar-pdf/<int:id>")
def gerar_pdf(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT m.data, m.valor, v.placa, m.oficina, m.descricao, m.quantidade, m.validade
    FROM manutencoes m
    JOIN veiculos v ON m.veiculo_id = v.id
    WHERE m.id=%s
    """, (id,))

    d = cursor.fetchone()

    if d:
        caminho = os.path.join(PDF_FOLDER, f"manutencao_{id}.pdf")

        c = canvas.Canvas(caminho)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 820, "RELATÓRIO DE MANUTENÇÃO")

        c.setStrokeColor(colors.blue)
        c.setLineWidth(3)
        c.line(100, 810, 450, 810)

        c.setFont("Helvetica", 12)
        c.drawString(100, 770, f"Data: {d[0]}")
        c.drawString(100, 750, f"Valor: R$ {d[1]}")
        c.drawString(100, 730, f"Veículo: {d[2]}")
        c.drawString(100, 710, f"Oficina: {d[3]}")
        c.drawString(100, 690, f"Descrição: {d[4]}")
        c.drawString(100, 670, f"Quantidade: {d[5]}")
        c.drawString(100, 650, f"Validade: {d[6]}")

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.green)
        c.drawString(100, 600, "✔ REGISTRADO COM SUCESSO")

        c.save()

    cursor.close()
    devolver_conexao(conn)

    return redirect(f"/baixar-pdf/{id}")


# ================= BAIXAR PDF =================
@manutencoes_bp.route("/baixar-pdf/<int:id>")
def baixar_pdf(id):

    caminho = os.path.join(PDF_FOLDER, f"manutencao_{id}.pdf")

    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    else:
        return container("<p>PDF não encontrado.</p>")
