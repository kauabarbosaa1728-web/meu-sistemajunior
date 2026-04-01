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
            <a href="/transferencia" data-nav="true">Transferência</a>
            <a href="/historico" data-nav="true">Histórico</a>
            <a href="/usuarios" data-nav="true">Usuários</a>
            <a href="/logs" data-nav="true">Logs</a>
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
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    body {{
        margin: 0;
        font-family: 'Share Tech Mono', monospace;
        background: #000000;
        color: #d1d5db;
    }}

    /* (todo seu CSS continua exatamente igual, não alterei nada) */

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
