def montar_alerta_estoque_baixo(baixo):
    alerta_html = ""

    if baixo:
        alerta_html += """
        <div class="alerta">
            <b>⚠️ Estoque baixo:</b><br>
        """

        for p, q in baixo:
            alerta_html += f"<span>{p} - {q} unidades</span><br>"

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
            <td>{c or '-'}</td>
            <td>R$ {float(v or 0):,.2f}</td>
            <td>
                <a href="/editar_estoque/{i}" class="btn-edit">✏️</a>
                <a href="/excluir_estoque/{i}" class="btn-del" onclick="return confirm('Tem certeza?')">🗑️</a>
            </td>
        </tr>
        """

    return tabela


def render_estoque(aviso, alerta_html, total_qtd, total_valor, tabela, msg):
    return f"""
    {aviso}
    {alerta_html}

    <h2 class="titulo">📦 ESTOQUE</h2>

    <div class="acoes-topo">
        <a href="/exportar_estoque" class="btn green">📥 Excel</a>
        <a href="/exportar_pdf" class="btn red">📄 PDF</a>
    </div>

    <div class="kpis">
        <div class="kpi">
            <span>Total de Produtos</span>
            <h2>{total_qtd}</h2>
        </div>

        <div class="kpi">
            <span>Valor em Estoque</span>
            <h2>R$ {total_valor:,.2f}</h2>
        </div>
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

    .titulo {{
        margin-bottom:15px;
    }}

    .acoes-topo {{
        margin-bottom:15px;
    }}

    .btn {{
        padding:10px 14px;
        border-radius:6px;
        text-decoration:none;
        color:white;
        margin-right:10px;
        display:inline-block;
    }}

    .green {{ background:#16a34a; }}
    .red {{ background:#dc2626; }}

    .kpis {{
        display:flex;
        gap:20px;
        margin-bottom:20px;
    }}

    .kpi {{
        flex:1;
        background:#0b0b0b;
        border:1px solid #2c2c2c;
        padding:20px;
        border-radius:10px;
    }}

    .kpi span {{
        color:#aaa;
        font-size:13px;
    }}

    .kpi h2 {{
        margin-top:5px;
        font-size:26px;
    }}

    .grid {{
        display:grid;
        grid-template-columns:320px 1fr;
        gap:20px;
    }}

    .box {{
        background:#0b0b0b;
        border:1px solid #2c2c2c;
        padding:20px;
        border-radius:10px;
    }}

    input {{
        width:100%;
        padding:10px;
        margin-bottom:10px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    button {{
        width:100%;
        padding:10px;
        background:#3b82f6;
        border:none;
        border-radius:6px;
        color:white;
        cursor:pointer;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
        margin-top:10px;
    }}

    th {{
        background:#1a1a1a;
        padding:10px;
        text-align:left;
    }}

    td {{
        padding:10px;
        border-top:1px solid #333;
    }}

    tr:hover {{
        background:#111;
    }}

    .btn-edit {{
        color:#3b82f6;
        margin-right:10px;
    }}

    .btn-del {{
        color:#ef4444;
    }}

    .alerta {{
        background:#330000;
        padding:10px;
        border-radius:8px;
        margin-bottom:15px;
        color:#ff4d4d;
    }}

    @media (max-width:900px) {{
        .grid {{
            grid-template-columns:1fr;
        }}

        .kpis {{
            flex-direction:column;
        }}
    }}

    </style>
    """
