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
                    <li><a href="/historico">📜 Histórico</a></li>
                    <li><a href="/historico_estoque">📦 Estoque</a></li>
                </ul>
            </li>

            <!-- 🔥 NOVO MENU VEÍCULOS -->
            <li class="has-submenu">
                <span class="menu-toggle">🚗 Veículos</span>
                <ul class="submenu">
                    <li><a href="/veiculos">📋 Ver Veículos</a></li>
                    <li><a href="/manutencoes">🔧 Manutenções</a></li>
                    <li><a href="/dashboard-veiculos">📊 Dashboard</a></li>
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
            letter-spacing: 0.4px;
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

        .logout:hover {{
            background: rgba(239,68,68,0.12) !important;
            box-shadow: inset 0 0 0 1px rgba(239,68,68,0.22) !important;
        }}

        .submenu {{
            display: none;
            position: absolute;
            top: calc(100% + 6px);
            left: 0;
            background: rgba(11,15,26,0.96);
            list-style: none;
            padding: 6px 0;
            margin: 0;
            min-width: 190px;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            overflow: hidden;
            z-index: 99999;
            box-shadow: 0 18px 40px rgba(0,0,0,0.45);
            backdrop-filter: blur(12px);
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
            background: rgba(59,130,246,0.15);
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
            background: linear-gradient(145deg, rgba(10,15,26,0.96), rgba(5,7,13,0.98));
            border: 1px solid rgba(255,255,255,0.08);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 15px;
            box-shadow: 0 14px 35px rgba(0,0,0,0.28);
            transition: 0.22s ease;
        }}

        .card:hover {{
            border-color: rgba(59,130,246,0.32);
            box-shadow: 0 18px 42px rgba(0,0,0,0.38), 0 0 18px rgba(59,130,246,0.10);
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
            outline: none;
            transition: 0.2s ease;
        }}

        input:focus,
        select:focus {{
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.18);
        }}

        button {{
            background: linear-gradient(135deg, #ffffff, #dbeafe);
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }}

        button:hover {{
            background: linear-gradient(135deg, #f8fafc, #bfdbfe);
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(59,130,246,0.22);
        }}

        a {{
            color: #38bdf8;
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
