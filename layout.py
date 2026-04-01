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


# ✅ CORREÇÃO PRINCIPAL (isso que quebrava tudo)
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
        <meta http-equiv="Cache-Control" content="public, max-age=300">
        <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
    </head>
    """ + topo() + f"""
    <div class="overlay" id="mainContent">
        {c}
    </div>
    """
