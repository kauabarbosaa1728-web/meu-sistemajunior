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
            background: #05070d;
            color: #d1d5db;
        }}

        /* NAVBAR */
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: #0a0f1a;
            border-bottom: 1px solid rgba(0,255,150,0.1);
            flex-wrap: wrap;
            backdrop-filter: blur(10px);
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
            color: #00ff9c;
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
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: 0.2s;
        }}

        .menu li:hover {{
            background: rgba(0,255,150,0.08);
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
            background: #0b0f1a;
            list-style: none;
            padding: 0;
            min-width: 180px;
            border: 1px solid rgba(0,255,150,0.1);
            border-radius: 10px;
            overflow: hidden;
            z-index: 99;
        }}

        .submenu li {{
            padding: 10px;
            font-size: 13px;
        }}

        .submenu li:hover {{
            background: rgba(0,255,150,0.08);
        }}

        .menu li:hover > .submenu {{
            display: block;
        }}

        .logout {{
            color: #ff4d4d !important;
        }}

        /* CONTEÚDO */
        .conteudo {{
            padding: 20px;
            max-width: 1400px;
            margin: auto;
        }}

        /* CARD */
        .card {{
            background: linear-gradient(145deg, #0a0f1a, #05070d);
            border: 1px solid rgba(0,255,150,0.08);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 15px;

            box-shadow:
                0 0 20px rgba(0,255,150,0.05),
                inset 0 0 10px rgba(0,255,150,0.03);

            transition: 0.3s;
        }}

        .card:hover {{
            transform: translateY(-4px);
            box-shadow:
                0 0 30px rgba(0,255,150,0.12),
                inset 0 0 15px rgba(0,255,150,0.05);
        }}

        .card h2, .card h3 {{
            color: #00ff9c;
        }}

        .erro {{
            color: #ff4d4d;
        }}

        /* GRID */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}

        /* INPUTS */
        input, select, button {{
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border-radius: 10px;
            border: 1px solid #1f2937;
            font-size: 14px;
            background: #0b0f1a;
            color: #fff;
        }}

        button {{
            background: #00ff9c;
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }}

        button:hover {{
            background: #00cc7a;
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
