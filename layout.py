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

            <li class="has-submenu">
                <span class="menu-toggle">📦 Estoque</span>
                <ul class="submenu">
                    <li><a href="/estoque">Ver Estoque</a></li>
                    <li><a href="/transferencia">Transferência</a></li>
                </ul>
            </li>

            <li class="has-submenu">
                <span class="menu-toggle">💰 Financeiro</span>
                <ul class="submenu">
                    <li><a href="/financeiro">Ver Financeiro</a></li>
                </ul>
            </li>

            <li class="has-submenu">
                <span class="menu-toggle">📄 Relatórios</span>
                <ul class="submenu">
                    <li><a href="/historico">Histórico</a></li>
                </ul>
            </li>

            <li class="has-submenu">
                <span class="menu-toggle">⚙️ Sistema</span>
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

        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: 'Inter', Arial;
            background: #05070d;
            color: #e5e7eb;
        }}

        .navbar {{
            position: relative;
            z-index: 99999;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: #0a0f1a;
            border-bottom: 1px solid rgba(255,255,255,0.08);
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
            color: #ffffff;
        }}

        .menu {{
            list-style: none;
            display: flex;
            gap: 10px;
            margin: 0;
            padding: 0;
            flex-wrap: wrap;
            align-items: center;
        }}

        .menu li {{
            position: relative;
            border-radius: 8px;
            font-size: 14px;
        }}

        .menu a,
        .menu-toggle {{
            display: block;
            padding: 8px 12px;
            text-decoration: none;
            color: #d1d5db;
            cursor: pointer;
            border-radius: 8px;
            user-select: none;
        }}

        .menu a:hover,
        .menu-toggle:hover {{
            background: rgba(255,255,255,0.08);
        }}

        .logout {{
            color: #ff4d4d !important;
        }}

        .submenu {{
            display: none;
            position: absolute;
            top: calc(100% + 6px);
            left: 0;
            background: #0b0f1a;
            list-style: none;
            padding: 6px 0;
            margin: 0;
            min-width: 190px;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            overflow: hidden;
            z-index: 99999;
            box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        }}

        .has-submenu.open > .submenu {{
            display: block;
        }}

        .submenu li {{
            width: 100%;
        }}

        .submenu a {{
            display: block;
            width: 100%;
            padding: 10px 14px;
            border-radius: 0;
            white-space: nowrap;
        }}

        .submenu a:hover {{
            background: rgba(255,255,255,0.08);
        }}

        .conteudo {{
            position: relative;
            z-index: 1;
            padding: 20px;
            max-width: 1400px;
            margin: auto;

            opacity: 0;
            transform: translateY(10px);
            animation: fadeIn 0.4s ease forwards;
        }}

        @keyframes fadeIn {{
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .card {{
            background: linear-gradient(145deg, #0a0f1a, #05070d);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 15px;
        }}

        .erro {{
            color: #ff4d4d;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}

        input, select, button {{
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border-radius: 10px;
            border: 1px solid #1f2937;
            background: #0b0f1a;
            color: #fff;
        }}

        button {{
            background: #ffffff;
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }}

        button:hover {{
            background: #e5e5e5;
        }}

        @media (max-width: 768px) {{
            .navbar {{
                align-items: flex-start;
            }}

            .menu {{
                width: 100%;
                flex-direction: column;
                align-items: stretch;
                margin-top: 10px;
                gap: 6px;
            }}

            .menu li {{
                width: 100%;
            }}

            .menu a,
            .menu-toggle {{
                width: 100%;
            }}

            .submenu {{
                position: static;
                margin-top: 6px;
                width: 100%;
                min-width: unset;
                box-shadow: none;
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

        <script>
        document.querySelectorAll(".menu-toggle").forEach(function(toggle) {{
            toggle.addEventListener("click", function(e) {{
                e.stopPropagation();

                const parent = this.parentElement;
                const isOpen = parent.classList.contains("open");

                document.querySelectorAll(".has-submenu").forEach(function(item) {{
                    item.classList.remove("open");
                }});

                if (!isOpen) {{
                    parent.classList.add("open");
                }}
            }});
        }});

        document.addEventListener("click", function(e) {{
            if (!e.target.closest(".navbar")) {{
                document.querySelectorAll(".has-submenu").forEach(function(item) {{
                    item.classList.remove("open");
                }});
            }}
        }});
        </script>

    </body>
    </html>
    """
