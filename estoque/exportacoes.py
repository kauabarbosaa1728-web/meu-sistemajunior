from flask import send_file
from openpyxl import Workbook
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from .repository import buscar_estoque_exportacao


def gerar_excel_estoque():
    dados = buscar_estoque_exportacao()

    wb = Workbook()
    ws = wb.active
    ws.title = "Estoque"

    ws.append(["Produto", "Qtd", "Categoria", "Valor Unitário", "Total"])

    total = 0

    for p, q, c, v in dados:
        t = q * float(v or 0)
        total += t
        ws.append([p, q, c, float(v or 0), t])

    ws.append([])
    ws.append(["", "", "", "TOTAL", total])

    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)

    return send_file(
        arquivo,
        as_attachment=True,
        download_name="estoque.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def gerar_pdf_estoque():
    dados = buscar_estoque_exportacao()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    styles = getSampleStyleSheet()

    try:
        elementos.append(Image("static/logo.png", width=60, height=60))
    except Exception:
        pass

    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph("<b>KBSISTEMAS</b>", styles["Title"]))
    elementos.append(Paragraph("Relatório Profissional de Estoque", styles["Heading2"]))
    elementos.append(Spacer(1, 20))

    tabela_dados = [["Produto", "Qtd", "Categoria", "Valor Unitário", "Total"]]

    total = 0

    for p, q, c, v in dados:
        t = q * float(v or 0)
        total += t

        tabela_dados.append([
            p,
            q,
            c or "-",
            f"R$ {float(v or 0):.2f}",
            f"R$ {t:.2f}"
        ])

    tabela = Table(tabela_dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elementos.append(tabela)
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph(f"<b>Total: R$ {total:.2f}</b>", styles["Heading2"]))

    doc.build(elementos)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="relatorio.pdf",
        mimetype="application/pdf"
    )
