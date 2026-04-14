def acesso_negado():
    return container("""
    <div class="card">
        <h2 class="erro">⛔ Você não tem autorização para acessar esta área.</h2>
        <p>Fale com um administrador para liberar esta permissão.</p>
        <p><a href="/painel">⬅ Voltar para o painel</a></p>
    </div>
    """)


def topo():
    return """
    <div class="navbar">
        <div class="logo-area">
            <img src="/static/logo.png" class="logo" alt="Logo KBSISTEMAS">
            <span class="logo-text">KBSISTEMAS</span>
        </div>

        <div class="menu">
            <a href="/painel" data-nav="true">Painel</a>
            <a href="/estoque" data-nav="true">Estoque</a>
            <a href="/financeiro" data-nav="true">💰 Financeiro</a>
            <a href="/transferencia" data-nav="true">Transferência</a>
            <a href="/historico" data-nav="true">Histórico</a>
            <a href="/usuarios" data-nav="true">Usuários</a>
            <a href="/logs" data-nav="true">Logs</a>
            <a href="/ia" data-nav="true">🤖 IA</a>
            <a href="/logout" class="logout">Sair</a>
        </div>
    </div>
    """


def container(c):
    return f"""
    <html>
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">

        <style>
        body {{
            margin: 0;
            font-family: Arial;
            background: #000;
            color: #d1d5db;
        }}

        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #0a0a0a;
            border-bottom: 1px solid #2a2a2a;
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .logo {{
            width: 35px;
            height: 35px;
            border-radius: 8px;
        }}

        .logo-text {{
            font-weight: bold;
            font-size: 18px;
        }}

        .menu a {{
            margin-right: 10px;
            padding: 6px 10px;
            border-radius: 8px;
            text-decoration: none;
            color: #ccc;
        }}

        .menu a:hover {{
            background: #1a1a1a;
            color: #fff;
        }}

        .logout {{
            color: red !important;
        }}

        .card {{
            background: #0b0b0b;
            border: 1px solid #2c2c2c;
            padding: 20px;
            border-radius: 10px;
        }}

        .erro {{
            color: #f87171;
        }}

        </style>
    </head>

    <body>
        {topo()}

        <div style="padding:20px;">
            {c}
        </div>
    </body>
    </html>
    """
