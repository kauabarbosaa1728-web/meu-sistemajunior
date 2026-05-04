def acesso_negado():
    return container("""
    <div class="card">
        <h2 class="erro">⛔ Acesso negado</h2>
        <p>Você não tem permissão para acessar esta área.</p>
        <p><a href="/painel">⬅ Voltar para o painel</a></p>
    </div>
    """)


def topo():
   return f"""
    <div class="navbar">

        <!-- LOGO -->
        <div class="logo-area">
            <img src="/static/logo.png" class="logo">
            <span class="logo-text">KBSISTEMAS</span>
        </div>

        <!-- MENU -->
        <ul class="menu">

            <li><a href="/painel">📊 Painel</a></li>

            <!-- ESTOQUE -->
            <li class="has-submenu">
                <span class="menu-toggle">📦 Estoque</span>
                <ul class="submenu">
                    <li><a href="/estoque">Ver Estoque</a></li>
                    <li><a href="/transferencia">Transferência</a></li>
                </ul>
            </li>

            <!-- 💰 FINANCEIRO (ADICIONADO MAIS OPÇÕES) -->
            <li class="has-submenu">
                <span class="menu-toggle">💰 Financeiro</span>
                <ul class="submenu">
                    <li><a href="/financeiro">💰 Ver Financeiro</a></li>

                    <li><a href="/relatorio-financeiro">📊 Relatório</a></li>

                    <li><a href="/entrada-financeiro">➕ Entradas</a></li>

                    <li><a href="/saida-financeiro">➖ Saídas</a></li>

                    <li><a href="/resumo-financeiro">📈 Resumo Geral</a></li>
                </ul>
            </li>

            <!-- RELATÓRIOS -->
            <li class="has-submenu">
                <span class="menu-toggle">📄 Relatórios</span>
                <ul class="submenu">
                    <li><a href="/historico">📜 Histórico</a></li>
                    <li><a href="/relatorio-geral">📊 Geral</a></li>
                    <li><a href="/historico_estoque">📦 Estoque</a></li>
                    <li><a href="/relatorio-veiculos">🚗 Veículos</a></li>
                    <li><a href="/relatorio-financeiro">💸 Financeiro</a></li>
                    <li><a href="/relatorio-problemas">🚨 Problemas</a></li>
                </ul>
            </li>

            <!-- VEÍCULOS -->
            <li class="has-submenu">
                <span class="menu-toggle">🚗 Veículos</span>
                <ul class="submenu">
                    <li><a href="/veiculos">📋 Ver Veículos</a></li>
                    <li><a href="/manutencoes">🔧 Manutenções</a></li>
                    <li><a href="/dashboard-veiculos">📊 Dashboard</a></li>
                </ul>
            </li>

            <!-- SISTEMA -->
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
    return """
    <html>
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" href="/static/logo.png">

        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <!-- FONTES -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">

        <!-- CHART -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: 'Inter', Arial;
            background: #05070d;
            background:
                radial-gradient(circle at top left, rgba(59,130,246,0.14), transparent 32%),
                radial-gradient(circle at top right, rgba(56,189,248,0.10), transparent 30%),
                #05070d;
            color: #e5e7eb;
        }}

        /* NAVBAR */
        .navbar {{
            position: relative;
            z-index: 99999;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: rgba(10,15,26,0.88);
            border-bottom: 1px solid rgba(255,255,255,0.08);
            flex-wrap: wrap;
            backdrop-filter: blur(14px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.35);
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
            box-shadow: 0 0 16px rgba(59,130,246,0.35);
        }}

        .logo-text {{
            font-weight: 600;
            font-size: 16px;
            color: #ffffff;
        }}

        /* MENU */
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
            transition: 0.22s ease;
        }}

        .menu a:hover,
        .menu-toggle:hover {{
            background: rgba(59,130,246,0.16);
            color: #ffffff;
            box-shadow: inset 0 0 0 1px rgba(59,130,246,0.18);
        }}

        .logout {{
            color: #ff4d4d !important;
        }}

        /* SUBMENU */
        .submenu {{
            display: none;
            position: absolute;
            top: calc(100% + 6px);
            left: 0;
            background: rgba(11,15,26,0.96);
            list-style: none;
            padding: 6px 0;
            min-width: 190px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .has-submenu.open > .submenu {{
            display: block;
        }}

        .submenu a {{
            padding: 10px 14px;
        }}

        /* CONTEÚDO */
        .conteudo {{
            padding: 20px;
            max-width: 1400px;
            margin: auto;
        }}

        /* CARD */
        .card {{
            background: linear-gradient(145deg, rgba(10,15,26,0.96), rgba(5,7,13,0.98));
            border: 1px solid rgba(255,255,255,0.08);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 15px;
        }}

        .erro {{
            color: #ff4d4d;
        }}

        /* INPUTS */
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
            background: linear-gradient(135deg, #ffffff, #dbeafe);
            color: #000;
            font-weight: bold;
            cursor: pointer;
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
        });

        document.addEventListener("click", function(e) {{
            if (!e.target.closest(".navbar")) {{
                document.querySelectorAll(".has-submenu").forEach(function(item) {{
                    item.classList.remove("open");
                }});
            }}
        });
        </script>

    </body>
    </html>
    """
