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


def render_editar_estoque(dado):
    return f"""
    <div class="card">
    <h2>✏️ EDITAR PRODUTO</h2>

    <form method="POST" style="display:flex; gap:10px; flex-wrap:wrap;">
        <input name="produto" value="{dado[0]}" placeholder="Produto">
        <input name="qtd" value="{dado[1]}" placeholder="Quantidade">
        <input name="categoria" value="{dado[2]}" placeholder="Categoria">
        <input name="valor" value="{float(dado[3] or 0):.2f}" placeholder="Valor (R$)">
        <button>Salvar</button>
    </form>
    </div>
    """


def render_produto_nao_encontrado():
    return """
    <div class="card">
    <h2 style='color:red'>❌ Produto não encontrado</h2>
    <a href="/estoque">⬅ Voltar</a>
    </div>
    """


def render_erro_atualizar(e):
    return f"""
    <div class="card">
    <h2 style='color:red'>❌ Erro ao atualizar</h2>
    <p>{e}</p>
    <a href="/estoque">⬅ Voltar</a>
    </div>
    """


def render_transferencia(produtos, usuarios, historico, msg):
    lista_produtos = "".join([f"<option value='{p}'>{p}</option>" for p in produtos])
    lista_usuarios = "".join([f"<option value='{u}'>{u}</option>" for u in usuarios])

    tabela = ""

    for h in historico:
        data_formatada = h[4].strftime("%d/%m/%Y %H:%M") if h[4] else "-"
        tabela += f"""
        <tr>
        <td>{h[0]}</td>
        <td>{h[1]}</td>
        <td>{h[2]}</td>
        <td>{h[3]}</td>
        <td>{data_formatada}</td>
        </tr>
        """

    return f"""
    <div class="wrap">

        <h2 style="margin-bottom:20px;">🔄 Transferência</h2>

        <div class="grid">

            <div class="box">
                <h3>Nova Transferência</h3>

                <form method="POST">

                    <label>Produto</label>
                    <select name="produto" required>
                        {lista_produtos}
                    </select>

                    <label>Quantidade</label>
                    <input name="qtd" type="number" min="1" required>

                    <label>Destino</label>
                    <select name="destino" required>
                        <option value="saida">Saída</option>
                        <option value="lixo">Lixo</option>
                        {lista_usuarios}
                    </select>

                    <button>🚀 Transferir</button>
                </form>

                <p>{msg}</p>
            </div>

            <div class="box">
                <h3>📜 Histórico</h3>

                <table>
                    <tr>
                        <th>Produto</th>
                        <th>Qtd</th>
                        <th>Destino</th>
                        <th>Usuário</th>
                        <th>Data</th>
                    </tr>
                    {tabela}
                </table>
            </div>

        </div>

    </div>

    <style>

    .wrap {{
        max-width: 1300px;
        margin: auto;
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

    label {{
        display:block;
        margin-top:10px;
        font-size:13px;
        color:#aaa;
    }}

    input, select {{
        width:100%;
        padding:10px;
        margin-top:5px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    button {{
        margin-top:15px;
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

    </style>
    """


def render_historico(busca, dados):
    tabela = ""

    for u, acao, det, data in dados:
        tabela += f"""
        <tr>
            <td>{u}</td>
            <td>{acao}</td>
            <td>{det}</td>
            <td>{data.strftime("%d/%m/%Y %H:%M:%S")}</td>
        </tr>
        """

    if not tabela:
        tabela = "<tr><td colspan='4'>Nenhum registro encontrado</td></tr>"

    return f"""
    <h2 style="margin-bottom:20px;">📜 Histórico do Sistema</h2>

    <form method="GET" style="margin-bottom:20px;">
        <input name="busca" placeholder="Buscar usuário, ação..." value="{busca}">
        <button>Buscar</button>
    </form>

    <div class="box">
        <table>
            <tr>
                <th>Usuário</th>
                <th>Ação</th>
                <th>Detalhes</th>
                <th>Data</th>
            </tr>
            {tabela}
        </table>
    </div>

    <style>

    input {{
        padding:10px;
        width:300px;
        background:#111;
        border:1px solid #333;
        color:white;
        border-radius:6px;
    }}

    button {{
        padding:10px;
        background:#3b82f6;
        border:none;
        color:white;
        border-radius:6px;
        cursor:pointer;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
        font-size:14px;
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

    </style>
    """


def render_entrada(msg, historico):
    tabela = ""

    for h in historico:
        tabela += f"""
        <tr>
        <td>{h[0]}</td>
        <td>{h[1]}</td>
        <td>{h[2]}</td>
        <td>R$ {float(h[3] or 0):,.2f}</td>
        <td>{h[4]}</td>
        <td>{h[5]}</td>
        </tr>
        """

    return f"""
    <div class="card">
    <h2>➕ ENTRADA DE PRODUTOS</h2>

    <form method="POST" style="display:flex; flex-direction:column; gap:10px;">
        <input name="produto" placeholder="Produto">
        <input name="qtd" placeholder="Quantidade">
        <input name="categoria" placeholder="Categoria">
        <input name="fornecedor" placeholder="Fornecedor">
        <input name="valor" placeholder="Valor (R$)">
        <button>Adicionar</button>
    </form>

    <p>{msg}</p>

    <a href="/estoque">⬅ Voltar para estoque</a>
    </div>

    <div class="card">
    <h2>📊 HISTÓRICO DE ENTRADAS</h2>

    <table>
    <tr>
    <th>Produto</th><th>Qtd</th><th>Fornecedor</th><th>Valor</th><th>User</th><th>Data</th>
    </tr>
    {tabela}
    </table>
    </div>
    """
