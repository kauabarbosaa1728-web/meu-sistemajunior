from flask import session
from banco import conectar, devolver_conexao

def carregar_permissoes(usuario):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT cargo,
               pode_estoque,
               pode_transferencia,
               pode_historico,
               pode_usuarios,
               pode_editar_estoque,
               pode_excluir_estoque,
               pode_logs,
               ativo,
               email,
               plano,
               nome_empresa
        FROM usuarios
        WHERE usuario=%s
        """, (usuario,))
        dado = cursor.fetchone()

        if dado:
            session["cargo"] = dado[0]

            # 🔥 SE FOR ADMIN → LIBERA TUDO
            if dado[0] == "admin":
                session["pode_estoque"] = True
                session["pode_transferencia"] = True
                session["pode_historico"] = True
                session["pode_usuarios"] = True
                session["pode_editar_estoque"] = True
                session["pode_excluir_estoque"] = True
                session["pode_logs"] = True
            else:
                session["pode_estoque"] = bool(dado[1])
                session["pode_transferencia"] = bool(dado[2])
                session["pode_historico"] = bool(dado[3])
                session["pode_usuarios"] = bool(dado[4])
                session["pode_editar_estoque"] = bool(dado[5])
                session["pode_excluir_estoque"] = bool(dado[6])
                session["pode_logs"] = bool(dado[7])

            session["ativo"] = bool(dado[8])
            session["email"] = dado[9] or ""
            session["plano"] = dado[10] or ""
            session["nome_empresa"] = dado[11] or ""

    finally:
        devolver_conexao(conn)


def tem_permissao(nome):
    # 🔥 ADMIN SEMPRE LIBERADO (SEGURANÇA EXTRA)
    if session.get("cargo") == "admin":
        return True

    return bool(session.get(nome, False))


def acesso_negado():
    return container("""
    <div class="card">
        <h2 class="erro">⛔ Você não tem autorização para acessar esta área.</h2>
        <p>Fale com um administrador para liberar esta permissão.</p>
        <p><a href="/painel">⬅ Voltar para o painel</a></p>
    </div>
    """)


def gerar_barras_3d(dados, altura_max=220, modo="quantidade"):
    if not dados:
        return '<div class="sem-dados">Sem dados para exibir.</div>'

    maiores = []
    for item in dados:
        valor = item[1]
        try:
            valor = int(valor or 0)
        except:
            valor = 0
        maiores.append(valor)

    max_valor = max(maiores) if maiores else 1
    if max_valor <= 0:
        max_valor = 1

    barras = ""
    for nome, valor in dados:
        try:
            valor = int(valor or 0)
        except:
            valor = 0

        altura = int((valor / max_valor) * altura_max)
        if valor > 0 and altura < 18:
            altura = 18

        if modo == "transferencia":
            cor_frente = "#8b8b8b"
            cor_lado = "#5d5d5d"
            cor_topo = "#bfbfbf"
        else:
            cor_frente = "#a3a3a3"
            cor_lado = "#737373"
            cor_topo = "#d4d4d4"

        barras += f"""
        <div class="bar-3d-item">
            <div class="bar-value">{valor}</div>
            <div class="bar-3d-wrap" style="height:{altura}px;">
                <div class="bar-3d-front" style="height:{altura}px; background:{cor_frente};"></div>
                <div class="bar-3d-side" style="height:{altura}px; background:{cor_lado};"></div>
                <div class="bar-3d-top" style="background:{cor_topo};"></div>
            </div>
            <div class="bar-label">{nome}</div>
        </div>
        """
    return barras


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
            <a href="/financeiro" data-nav="true">💰 Financeiro</a> <!-- 🔥 ADICIONADO -->
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
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">
        <meta http-equiv="Cache-Control" content="public, max-age=300">
    </head>
    """ + topo() + f"""
    .logo-text {{
        font-size: 18px;
        color: #e5e7eb;
        font-weight: bold;
        letter-spacing: 1px;
    }}

    .menu {{
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }}

    .menu a {{
        margin-right: 0;
        padding: 8px 12px;
        border-radius: 10px;
        transition: 0.2s;
        border: 1px solid transparent;
        color: #cfcfcf;
    }}

    .menu a:hover {{
        background: #1a1a1a;
        color: #ffffff;
        text-decoration: none;
        border-color: #3a3a3a;
    }}

    .logout {{
        color: #f87171 !important;
        border: 1px solid #4a2020 !important;
    }}

    .logout:hover {{
        background: #2a1111 !important;
        color: #ffb4b4 !important;
        border-color: #6a2a2a !important;
    }}

    .overlay {{
        padding: 20px;
        min-height: 100vh;
        background: #000000;
    }}

    a {{
        color: #d1d5db;
        text-decoration: none;
        margin-right: 15px;
    }}

    a:hover {{
        color: #ffffff;
        text-decoration: underline;
    }}

    input, button, select, textarea {{
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        border: 1px solid #3a3a3a;
        background: #111111;
        color: #e5e7eb;
        font-family: 'Share Tech Mono', monospace;
    }}

    textarea {{
        width: 100%;
        min-height: 80px;
    }}

    input[type="checkbox"] {{
        width: auto;
        transform: scale(1.1);
        margin-right: 8px;
    }}

    button {{
        cursor: pointer;
        transition: 0.2s;
        background: #161616;
    }}

    button:hover {{
        background: #2a2a2a;
        color: #ffffff;
        border-color: #5a5a5a;
        font-weight: bold;
    }}

    table {{
        width: 100%;
        background: #0d0d0d;
        border-collapse: collapse;
        margin-top: 15px;
    }}

    th, td {{
        padding: 10px;
        border: 1px solid #2f2f2f;
        text-align: left;
        vertical-align: top;
    }}

    th {{
        background: #151515;
        color: #f3f4f6;
    }}

    .card {{
        background: #0b0b0b;
        border: 1px solid #2c2c2c;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        color: #e5e7eb;
    }}

    .cards {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }}

    .mini-card {{
        background: linear-gradient(180deg, #121212 0%, #070707 100%);
        border: 1px solid #3a3a3a;
        border-radius: 14px;
        padding: 20px;
        color: #e5e7eb;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }}

    .mensagem {{
        margin-top: 10px;
        font-weight: bold;
        color: #d1d5db;
    }}

    .erro {{
        color: #f87171;
        font-weight: bold;
    }}

    .sucesso {{
        color: #86efac;
        font-weight: bold;
    }}

    .btn-danger {{
        color: #f87171;
        border-color: #7f1d1d;
    }}

    .btn-danger:hover {{
        background: #2a1111;
        color: #ffffff;
    }}

    .btn-warning {{
        color: #facc15;
        border-color: #5a4a12;
    }}

    .btn-warning:hover {{
        background: #2a2410;
        color: #ffffff;
    }}

    .btn-edit {{
        color: #d1d5db;
        border: 1px solid #4a4a4a;
        padding: 6px 10px;
        border-radius: 8px;
        display: inline-block;
    }}

    .btn-edit:hover {{
        background: #1f1f1f;
        color: #ffffff;
        text-decoration: none;
    }}

    .permissoes-box {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 8px;
        margin-top: 10px;
    }}

    .perm-item {{
        background: #111111;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #2f2f2f;
    }}

    .page-loader {{
        position: fixed;
        top: 0;
        left: 0;
        height: 2px;
        width: 0%;
        background: linear-gradient(90deg, #888888, #ffffff);
        z-index: 9999;
        transition: width 0.2s ease;
    }}

    .dashboard-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 20px;
    }}

    .chart-3d-card {{
        background: linear-gradient(180deg, #101010 0%, #060606 100%);
        border: 1px solid #2d2d2d;
        border-radius: 14px;
        padding: 20px;
    }}

    .chart-title {{
        font-size: 18px;
        font-weight: bold;
        color: #f3f4f6;
        margin-bottom: 20px;
    }}

    .chart-3d-area {{
        height: 320px;
        display: flex;
        align-items: flex-end;
        gap: 18px;
        padding: 15px 10px 5px 10px;
        border-left: 1px solid #303030;
        border-bottom: 1px solid #303030;
        background:
            repeating-linear-gradient(
                to top,
                rgba(255,255,255,0.03) 0px,
                rgba(255,255,255,0.03) 1px,
                transparent 1px,
                transparent 52px
            );
        overflow-x: auto;
        overflow-y: hidden;
    }}

    .bar-3d-item {{
        min-width: 72px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
    }}

    .bar-value {{
        font-size: 12px;
        color: #f3f4f6;
        font-weight: bold;
    }}

    .bar-3d-wrap {{
        position: relative;
        width: 34px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }}

    .bar-3d-front {{
        width: 34px;
        position: relative;
        border-radius: 3px 3px 0 0;
        box-shadow: inset -4px 0 0 rgba(0,0,0,0.15);
    }}

    .bar-3d-side {{
        position: absolute;
        right: -10px;
        bottom: 0;
        width: 10px;
        transform: skewY(45deg);
        transform-origin: left bottom;
        border-radius: 0 3px 0 0;
        opacity: 0.95;
    }}

    .bar-3d-top {{
        position: absolute;
        top: -10px;
        left: 0;
        width: 34px;
        height: 10px;
        transform: skewX(45deg);
        transform-origin: left bottom;
        border-radius: 3px 3px 0 0;
        opacity: 0.95;
    }}

    .bar-label {{
        font-size: 11px;
        color: #d1d5db;
        text-align: center;
        max-width: 85px;
        line-height: 1.25;
        word-break: break-word;
    }}

    .sem-dados {{
        color: #9ca3af;
        padding: 20px 0;
    }}

    .ranking-table td, .ranking-table th {{
        font-size: 13px;
    }}

    @media (max-width: 1100px) {{
        .dashboard-grid {{
            grid-template-columns: 1fr;
        }}
    }}

    @media (max-width: 900px) {{
        .navbar {{
            flex-direction: column;
            align-items: flex-start;
        }}

        .menu {{
            width: 100%;
        }}
    }}
    </style>

    <div class="page-loader" id="pageLoader"></div>

    <div class="overlay" id="mainContent">
        {c}
    </div>

    <script>
    (function() {{
        const loader = document.getElementById("pageLoader");

        function startLoader() {{
            if (loader) {{
                loader.style.width = "35%";
            }}
        }}

        function finishLoader() {{
            if (loader) {{
                loader.style.width = "100%";
                setTimeout(() => {{
                    loader.style.width = "0%";
                }}, 180);
            }}
        }}

        async function navegar(url, salvarHistorico = true) {{
            try {{
                startLoader();
                const resposta = await fetch(url, {{
                    headers: {{
                        "X-Requested-With": "fetch"
                    }}
                }});

                const html = await resposta.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");

                const novoConteudo = doc.querySelector("#mainContent");
                const novoTitulo = doc.querySelector("title");

                if (novoConteudo) {{
                    document.querySelector("#mainContent").innerHTML = novoConteudo.innerHTML;
                }} else {{
                    window.location.href = url;
                    return;
                }}

                if (novoTitulo) {{
                    document.title = novoTitulo.innerText;
                }}

                if (salvarHistorico) {{
                    history.pushState({{ url: url }}, "", url);
                }}

                finishLoader();
            }} catch (e) {{
                window.location.href = url;
            }}
        }}

        document.addEventListener("click", function(e) {{
            const link = e.target.closest('a[data-nav="true"]');
            if (!link) return;

            const href = link.getAttribute("href");
            if (!href || href.startsWith("http") || href.startsWith("#")) return;

            e.preventDefault();
            navegar(href, true);
        }});

        window.addEventListener("popstate", function() {{
            navegar(location.pathname, false);
        }});
    }})();
    </script>
    """
