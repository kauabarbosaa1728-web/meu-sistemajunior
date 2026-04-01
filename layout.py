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

    .navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        padding: 12px 20px;
        background: #0a0a0a;
        border-bottom: 1px solid #2a2a2a;
        position: sticky;
        top: 0;
        z-index: 999;
    }}

    .logo-area {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .logo {{
        width: 38px;
        height: 38px;
        border-radius: 10px;
        object-fit: cover;
        border: 1px solid #2f2f2f;
        background: #111111;
    }}

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

    /* RESTO DO SEU CSS CONTINUA IGUAL */
    
    </style>

    <div class="page-loader" id="pageLoader"></div>

    <div class="overlay" id="mainContent">
        {c}
    </div>

    <script>
    (function() {{
        const loader = document.getElementById("pageLoader");

        function startLoader() {{
            if (loader) loader.style.width = "35%";
        }}

        function finishLoader() {{
            if (loader) {{
                loader.style.width = "100%";
                setTimeout(() => loader.style.width = "0%", 180);
            }}
        }}

        async function navegar(url, salvarHistorico = true) {{
            try {{
                startLoader();
                const resposta = await fetch(url, {{
                    headers: {{ "X-Requested-With": "fetch" }}
                }});

                const html = await resposta.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");

                const novoConteudo = doc.querySelector("#mainContent");

                if (novoConteudo) {{
                    document.querySelector("#mainContent").innerHTML = novoConteudo.innerHTML;
                }}

                finishLoader();
            }} catch {{
                window.location.href = url;
            }}
        }}

        document.addEventListener("click", function(e) {{
            const link = e.target.closest('a[data-nav="true"]');
            if (!link) return;

            e.preventDefault();
            navegar(link.getAttribute("href"));
        }});
    }})();
    </script>
    """
