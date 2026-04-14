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

        <ul class="menu">

            <li><a href="/painel" data-nav="true">Painel</a></li>

            <li>
                Estoque
                <ul class="submenu">
                    <li><a href="/estoque" data-nav="true">Ver Estoque</a></li>
                    <li><a href="/transferencia" data-nav="true">Transferência</a></li>
                </ul>
            </li>

            <li>
                Financeiro
                <ul class="submenu">
                    <li><a href="/financeiro" data-nav="true">💰 Financeiro</a></li>
                </ul>
            </li>

            <li>
                Relatórios
                <ul class="submenu">
                    <li><a href="/historico" data-nav="true">Histórico</a></li>
                </ul>
            </li>

            <li>
                Sistema
                <ul class="submenu">
                    <li><a href="/usuarios" data-nav="true">Usuários</a></li>
                    <li><a href="/logs" data-nav="true">Logs</a></li>
                    <li><a href="/ia" data-nav="true">🤖 IA</a></li>
                </ul>
            </li>

            <li><a href="/logout" class="logout">Sair</a></li>

        </ul>
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

        /* NAVBAR */
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

        /* MENU PRINCIPAL */
        .menu {{
            list-style: none;
            display: flex;
            gap: 15px;
            margin: 0;
            padding: 0;
        }}

        .menu li {{
            position: relative;
            padding: 6px 10px;
            border-radius: 8px;
            cursor: pointer;
            color: #ccc;
        }}

        .menu li:hover {{
            background: #1a1a1a;
            color: #fff;
        }}

        .menu a {{
            text-decoration: none;
            color: inherit;
        }}

        /* SUBMENU */
        .submenu {{
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            background: #111;
            list-style: none;
            padding: 0;
            min-width: 180px;
            border: 1px solid #2a2a2a;
            z-index: 999;
        }}

        .submenu li {{
            padding: 10px;
            border-bottom: 1px solid #222;
        }}

        .submenu li:hover {{
            background: #222;
        }}

        .menu li:hover > .submenu {{
            display: block;
        }}

        .logout {{
            color: red !important;
        }}

        /* CARD */
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
