def acesso_negado():
    return container("""
    <div class="card">
        <h2 class="erro">⛔ Acesso negado</h2>
        <p>Você não tem permissão para acessar esta área.</p>
        <p><a href="/painel">⬅ Voltar para o painel</a></p>
    </div>
    """)


def topo():
    return """
    <div class="navbar">
        <div class="logo-area">
            <img src="/static/logo.png" class="logo">
            <span class="logo-text">KBSISTEMAS</span>
        </div>

        <ul class="menu">

            <li><a href="/painel">📊 Painel</a></li>

            <li>
                📦 Estoque
                <ul class="submenu">
                    <li><a href="/estoque">Ver Estoque</a></li>
                    <li><a href="/transferencia">Transferência</a></li>
                </ul>
            </li>

            <li>
                💰 Financeiro
                <ul class="submenu">
                    <li><a href="/financeiro">Ver Financeiro</a></li>
                </ul>
            </li>

            <li>
                📄 Relatórios
                <ul class="submenu">
                    <li><a href="/historico">Histórico</a></li>
                </ul>
            </li>

            <li>
                ⚙️ Sistema
                <ul class="submenu">
                    <li><a href="/usuarios">Usuários</a></li>
                    <li><a href="/logs">Logs</a></li>
                    <li><a href="/ia">IA</a></li>
                </ul>
            </li>

            <li><a href="/logout" class="logout">🚪 Sair</a></li>

        </ul>
    </div>
    """


def container(c):
    return f"""
    <html>
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" href="/static/logo.png">

        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <!-- FONTE -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">

        <!-- CHART -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <style>

        body {{
            margin: 0;
            font-family: 'Inter', Arial;
            background: #000;
            color: #d1d5db;
        }}

        /* NAVBAR */
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: #0a0a0a;
            border-bottom: 1px solid #2a2a2a;
            flex-wrap: wrap;
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .logo {{
            width: 35px;
            height: 35px;
            border-radius: 6px;
        }}

        .logo-text {{
            font-weight: 600;
            font-size: 16px;
            color: #3b82f6;
        }}

        /* MENU */
        .menu {{
            list-style: none;
            display: flex;
            gap: 10px;
            margin: 0;
            padding: 0;
            flex-wrap: wrap;
        }}

        .menu li {{
            position: relative;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }}

        .menu li:hover {{
            background: #1a1a1a;
        }}

        .menu a {{
            text-decoration: none;
            color: #d1d5db;
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
            border-radius: 6px;
            overflow: hidden;
            z-index: 99;
        }}

        .submenu li {{
            padding: 10px;
            font-size: 13px;
        }}

        .submenu li:hover {{
            background: #222;
        }}

        .menu li:hover > .submenu {{
            display: block;
        }}

        .logout {{
            color: #ef4444 !important;
        }}

        /* CONTEÚDO */
        .conteudo {{
            padding: 15px;
            max-width: 1400px;
            margin: auto;
        }}

        /* CARD */
        .card {{
            background: #0b0b0b;
            border: 1px solid #2c2c2c;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }}

        .erro {{
            color: #f87171;
        }}

        /* INPUTS MOBILE */
        input, select, button {{
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
        }}

        button {{
            background: #3b82f6;
            color: white;
            cursor: pointer;
        }}

        button:hover {{
            background: #2563eb;
        }}

        /* RESPONSIVO */
        @media (max-width: 768px) {{

            .navbar {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .menu {{
                width: 100%;
                flex-direction: column;
                margin-top: 10px;
            }}

            .menu li {{
                width: 100%;
            }}

            .submenu {{
                position: relative;
                border: none;
            }}

            .conteudo {{
                padding: 10px;
            }}

        }}

        </style>
    </head>

    <body>

        {topo()}

        <div class="conteudo">
            {c}
        </div>

    </body>
    </html>
    """
