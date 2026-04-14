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
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">
        <meta http-equiv="Cache-Control" content="public, max-age=300">
    </head>
    """ + topo() + f"""
    <!-- TODO O RESTO DO SEU HTML/CSS/JS FICA AQUI IGUAL -->
    <div class="overlay" id="mainContent">
        {c}
    </div>
    """
