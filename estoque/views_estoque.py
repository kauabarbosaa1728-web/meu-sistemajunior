def montar_alerta_estoque_baixo(baixo):
    alerta_html = ""

    if baixo:
        alerta_html += """
        <div style="background:#330000;padding:10px;border-radius:8px;margin-bottom:15px;">
            <b>⚠️ Estoque baixo:</b><br>
        """

        for p, q in baixo:
            alerta_html += f"<span style='color:red'>{p} - {q} unidades</span><br>"

        alerta_html += "</div>"

    return alerta_html


def montar_tabela_estoque(dados):
    tabela = ""

    for i, p, q, c, v in dados:
        tabela += f"""
        <tr>
            <td>{i}</td>
            <td>{p}</td>
            <td>{q}</td>
            <td>{c or ''}</td>
            <td>R$ {float(v or 0):,.2f}</td>
            <td>
                <a href="/editar_estoque/{i}">✏️</a>
                <a href="/excluir_estoque/{i}" onclick="return confirm('Tem certeza?')">🗑️</a>
            </td>
        </tr>
        """

    return tabela


def render_estoque(aviso, alerta_html, total_qtd, total_valor, tabela, msg):
    return f"""
    {aviso}
    {alerta_html}

    <h2>📦 ESTOQUE</h2>

    <a href="/exportar_estoque" style="
        background:#16a34a;
        padding:10px;
        border-radius:6px;
        color:white;
        text-decoration:none;
        display:inline-block;
        margin-bottom:15px;
    ">
        📥 Excel
    </a>

    <a href="/exportar_pdf" style="
        background:#dc2626;
        padding:10px;
        border-radius:6px;
        color:white;
        text-decoration:none;
        display:inline-block;
        margin-bottom:15px;
        margin-left:10px;
    ">
        📄 PDF
    </a>

    <div style="background:#111;padding:15px;border-radius:8px;margin-bottom:20px;">
        <b>Quantidade total:</b> {total_qtd} <br>
        <b>Valor total:</b> R$ {total_valor:,.2f}
    </div>

    <div class="grid">
        <div class="box">
            <h3>➕ Novo Produto</h3>

            <form method="POST">
                <input name="produto" placeholder="Produto" required>
                <input name="qtd" placeholder="Quantidade" required>
                <input name="categoria" placeholder="Categoria">
                <input name="valor" placeholder="Valor (R$)">
                <button type="submit">Adicionar</button>
            </form>

            <p>{msg}</p>
        </div>

        <div class="box">
            <h3>📋 Produtos</h3>

            <table>
                <tr>
                    <th>ID</th>
                    <th>Produto</th>
                    <th>Qtd</th>
                    <th>Categoria</th>
                    <th>Valor</th>
                    <th>Ações</th>
                </tr>
                {tabela}
            </table>
        </div>
    </div>

    <style>
        .grid {{
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
        }}

        .box {{
            background: #0b0b0b;
            border: 1px solid #2c2c2c;
            padding: 20px;
            border-radius: 10px;
        }}

        input {{
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            background: #111;
            border: 1px solid #333;
            color: white;
            border-radius: 6px;
            box-sizing: border-box;
        }}

        button {{
            width: 100%;
            padding: 10px;
            background: #3b82f6;
            border: none;
            border-radius: 6px;
            color: white;
            cursor: pointer;
        }}

        button:hover {{
            opacity: 0.9;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #1a1a1a;
            padding: 10px;
            text-align: left;
        }}

        td {{
            padding: 10px;
            border-top: 1px solid #333;
        }}

        tr:hover {{
            background: #111;
        }}

        @media (max-width: 900px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
    """
