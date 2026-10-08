from flask import Blueprint, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
from banco import conectar, devolver_conexao, registrar_log
from layout import container, acesso_negado
from html import escape


usuarios_bp = Blueprint("usuarios_bp", __name__)


# ============================================================
# PERMISSÕES DISPONÍVEIS
# ============================================================

PERMISSOES = [

    # ========================================================
    # ESTOQUE
    # ========================================================

    ("pode_estoque", "📦 Estoque"),
    ("pode_transferencia", "🔄 Transferências"),
    ("pode_historico", "📋 Histórico"),
    ("pode_editar_estoque", "✏️ Editar estoque"),
    ("pode_excluir_estoque", "🗑️ Excluir estoque"),
    ("pode_entrada_estoque", "📥 Entrada de estoque"),
    ("pode_categorias", "📂 Categorias"),
    ("pode_fornecedores", "🏭 Fornecedores"),
    ("pode_ncm", "🔢 NCM"),
    ("pode_exportar_estoque", "📊 Exportar estoque"),
    ("pode_pdf_estoque", "📄 PDF do estoque"),

    # ========================================================
    # SISTEMA
    # ========================================================

    ("pode_usuarios", "👥 Usuários"),
    ("pode_logs", "📝 Logs"),

    # ========================================================
    # FINANCEIRO
    # ========================================================

    ("pode_financeiro", "💰 Financeiro"),
    ("pode_entrada_financeiro", "➕ Entrada financeira"),
    ("pode_saida_financeiro", "➖ Saída financeira"),
    ("pode_resumo_financeiro", "📊 Resumo financeiro"),
    ("pode_relatorio_financeiro", "📑 Relatório financeiro"),

    # ========================================================
    # VENDAS
    # ========================================================

    ("pode_vendas", "🛒 Vendas"),
    ("pode_historico_vendas", "📜 Histórico de vendas"),

    # ========================================================
    # RELATÓRIOS
    # ========================================================

    ("pode_relatorios", "📊 Relatórios"),
    ("pode_relatorio_geral", "📈 Relatório geral"),
    ("pode_relatorio_estoque", "📦 Relatório estoque"),
    ("pode_relatorio_veiculos", "🚗 Relatório veículos"),
    ("pode_relatorio_problemas", "⚠️ Relatório problemas"),

    # ========================================================
    # VEÍCULOS
    # ========================================================

    ("pode_veiculos", "🚙 Veículos"),
    ("pode_manutencoes", "🔧 Manutenções"),
    ("pode_dashboard", "📊 Dashboard veículos"),
    ("pode_rotas", "🗺️ Rotas"),

    # ========================================================
    # PROBLEMAS
    # ========================================================

    ("pode_problemas", "⚠️ Problemas"),
    ("pode_ocorrencias", "📋 Ocorrências"),
    ("pode_resolver_problemas", "✅ Resolver problemas"),
    ("pode_excluir_problemas", "🗑️ Excluir problemas"),
    ("pode_pdf_problemas", "📄 PDF problemas"),

    # ========================================================
    # OUTROS
    # ========================================================

    ("pode_ia", "🤖 Inteligência Artificial"),
    ("pode_configuracoes", "⚙️ Configurações"),
]


# ============================================================
# GRUPOS DE PERMISSÕES
# ============================================================

GRUPOS_PERMISSOES = [

    (
        "📦 ESTOQUE",
        [
            ("pode_estoque", "📦 Estoque"),
            ("pode_transferencia", "🔄 Transferências"),
            ("pode_historico", "📋 Histórico"),
            ("pode_editar_estoque", "✏️ Editar estoque"),
            ("pode_excluir_estoque", "🗑️ Excluir estoque"),
            ("pode_entrada_estoque", "📥 Entrada de estoque"),
            ("pode_categorias", "📂 Categorias"),
            ("pode_fornecedores", "🏭 Fornecedores"),
            ("pode_ncm", "🔢 NCM"),
            ("pode_exportar_estoque", "📊 Exportar estoque"),
            ("pode_pdf_estoque", "📄 PDF do estoque"),
        ]
    ),

    (
        "🖥️ SISTEMA",
        [
            ("pode_usuarios", "👥 Usuários"),
            ("pode_logs", "📝 Logs"),
        ]
    ),

    (
        "💰 FINANCEIRO",
        [
            ("pode_financeiro", "💰 Financeiro"),
            ("pode_entrada_financeiro", "➕ Entrada financeira"),
            ("pode_saida_financeiro", "➖ Saída financeira"),
            ("pode_resumo_financeiro", "📊 Resumo financeiro"),
            ("pode_relatorio_financeiro", "📑 Relatório financeiro"),
        ]
    ),

    (
        "🛒 VENDAS",
        [
            ("pode_vendas", "🛒 Vendas"),
            ("pode_historico_vendas", "📜 Histórico de vendas"),
        ]
    ),

    (
        "📊 RELATÓRIOS",
        [
            ("pode_relatorios", "📊 Relatórios"),
            ("pode_relatorio_geral", "📈 Relatório geral"),
            ("pode_relatorio_estoque", "📦 Relatório estoque"),
            ("pode_relatorio_veiculos", "🚗 Relatório veículos"),
            ("pode_relatorio_problemas", "⚠️ Relatório problemas"),
        ]
    ),

    (
        "🚙 VEÍCULOS",
        [
            ("pode_veiculos", "🚙 Veículos"),
            ("pode_manutencoes", "🔧 Manutenções"),
            ("pode_dashboard", "📊 Dashboard veículos"),
            ("pode_rotas", "🗺️ Rotas"),
        ]
    ),

    (
        "⚠️ PROBLEMAS",
        [
            ("pode_problemas", "⚠️ Problemas"),
            ("pode_ocorrencias", "📋 Ocorrências"),
            ("pode_resolver_problemas", "✅ Resolver problemas"),
            ("pode_excluir_problemas", "🗑️ Excluir problemas"),
            ("pode_pdf_problemas", "📄 PDF problemas"),
        ]
    ),

    (
        "🤖 OUTROS",
        [
            ("pode_ia", "🤖 Inteligência Artificial"),
            ("pode_configuracoes", "⚙️ Configurações"),
        ]
    ),
]


# ============================================================
# VERIFICAR ADMIN
# ============================================================

def usuario_eh_admin():

    return (
        "user" in session
        and session.get("cargo") == "admin"
    )


# ============================================================
# PEGAR PERMISSÕES DO FORMULÁRIO
# ============================================================

def pegar_permissoes_formulario():

    permissoes = {}

    for campo, _nome in PERMISSOES:

        permissoes[campo] = (
            1 if request.form.get(campo) else 0
        )

    return permissoes


# ============================================================
# ADMIN = ACESSO TOTAL
# ============================================================

def permissoes_admin():

    return {
        campo: 1
        for campo, _nome in PERMISSOES
    }


# ============================================================
# GERAR HTML DAS PERMISSÕES
# ============================================================

def gerar_permissoes_criacao():

    html = ""

    for titulo, permissoes in GRUPOS_PERMISSOES:

        html += f"""

        <div class="grupo-permissoes">

            <div class="grupo-titulo">
                {titulo}
            </div>

            <div class="grupo-grid">
        """

        for campo, nome in permissoes:

            html += f"""

                <label class="permissao-item">

                    <input
                        type="checkbox"
                        name="{campo}"
                    >

                    {nome}

                </label>

            """

        html += """

            </div>

        </div>

        """

    return html


# ============================================================
# GERAR HTML DAS PERMISSÕES DE EDIÇÃO
# ============================================================

def gerar_permissoes_edicao(usuario_dados):

    html = ""

    for titulo, permissoes in GRUPOS_PERMISSOES:

        html += f"""

        <div class="grupo-edicao">

            <div class="grupo-edicao-titulo">
                {titulo}
            </div>

        """

        for campo, nome in permissoes:

            valor = usuario_dados.get(campo, 0)

            checked = "checked" if valor else ""

            html += f"""

                <label class="permissao-edicao-item">

                    <input
                        type="checkbox"
                        name="{campo}"
                        {checked}
                    >

                    {nome}

                </label>

            """

        html += """

        </div>

        """

    return html


# ============================================================
# PÁGINA DE USUÁRIOS
# ============================================================

@usuarios_bp.route(
    "/usuarios",
    methods=["GET", "POST"]
)
def usuarios():

    if "user" not in session:
        return redirect("/")

    if not usuario_eh_admin():
        return acesso_negado()

    conn = conectar()

    if conn is None:
        return "Erro de conexão com o banco."

    cursor = conn.cursor()

    mensagem = ""
    tipo_mensagem = ""

    try:

        # ====================================================
        # CRIAR USUÁRIO
        # ====================================================

        if request.method == "POST":

            try:

                user = request.form.get(
                    "user",
                    ""
                ).strip()

                senha = request.form.get(
                    "senha",
                    ""
                ).strip()

                cargo = request.form.get(
                    "cargo",
                    "operador"
                ).strip().lower()

                email = request.form.get(
                    "email",
                    ""
                ).strip()

                nome_empresa = request.form.get(
                    "nome_empresa",
                    ""
                ).strip()

                plano = request.form.get(
                    "plano",
                    "basico"
                ).strip().lower()

                # --------------------------------------------
                # VALIDAÇÕES
                # --------------------------------------------

                if not user:
                    raise ValueError(
                        "Informe o nome do usuário."
                    )

                if not senha:
                    raise ValueError(
                        "Informe uma senha."
                    )

                if len(senha) < 4:
                    raise ValueError(
                        "A senha deve ter pelo menos 4 caracteres."
                    )

                if cargo not in (
                    "admin",
                    "operador"
                ):
                    cargo = "operador"

                if plano not in (
                    "basico",
                    "profissional",
                    "premium"
                ):
                    plano = "basico"

                # --------------------------------------------
                # VERIFICAR SE USUÁRIO JÁ EXISTE
                # --------------------------------------------

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM usuarios
                    WHERE LOWER(usuario) = LOWER(%s)
                    """,
                    (user,)
                )

                existe = cursor.fetchone()[0]

                if existe > 0:
                    raise ValueError(
                        "Esse usuário já existe."
                    )

                # --------------------------------------------
                # PERMISSÕES
                # --------------------------------------------

                if cargo == "admin":

                    permissoes = permissoes_admin()

                else:

                    permissoes = (
                        pegar_permissoes_formulario()
                    )

                # --------------------------------------------
                # COLUNAS DAS PERMISSÕES
                # --------------------------------------------

                campos_permissoes = ", ".join(
                    campo
                    for campo, _nome in PERMISSOES
                )

                valores_permissoes = ", ".join(
                    ["%s"] * len(PERMISSOES)
                )

                valores = [
                    user,
                    generate_password_hash(senha),
                    cargo,
                    email,
                    plano,
                    nome_empresa
                ]

                valores.extend(
                    permissoes[campo]
                    for campo, _nome in PERMISSOES
                )

                # --------------------------------------------
                # CRIAR USUÁRIO
                # --------------------------------------------

                cursor.execute(
                    f"""
                    INSERT INTO usuarios (
                        usuario,
                        senha,
                        cargo,
                        ativo,
                        email,
                        plano,
                        nome_empresa,
                        {campos_permissoes}
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        1,
                        %s,
                        %s,
                        %s,
                        {valores_permissoes}
                    )
                    """,
                    tuple(valores)
                )

                conn.commit()

                try:

                    registrar_log(
                        session.get(
                            "user",
                            "admin"
                        ),
                        f"Criou o usuário {user}"
                    )

                except Exception:
                    pass

                mensagem = (
                    "Usuário criado com sucesso!"
                )

                tipo_mensagem = "sucesso"

            except Exception as e:

                conn.rollback()

                mensagem = str(e)
                tipo_mensagem = "erro"

        # ====================================================
        # LISTAR USUÁRIOS
        # ====================================================

        campos_select = ", ".join(
            campo
            for campo, _nome in PERMISSOES
        )

        cursor.execute(
            f"""
            SELECT
                usuario,
                cargo,
                online,
                ativo,
                email,
                plano,
                nome_empresa,
                {campos_select}
            FROM usuarios
            ORDER BY
                CASE
                    WHEN usuario = 'admin'
                    THEN 0
                    ELSE 1
                END,
                usuario
            """
        )

        dados = cursor.fetchall()

        tabela = ""

        for linha in dados:

            # --------------------------------------------
            # DADOS BÁSICOS
            # --------------------------------------------

            usuario = linha[0]
            cargo = linha[1]
            online = linha[2]
            ativo = linha[3]
            email = linha[4]
            plano = linha[5]
            nome_empresa = linha[6]

            # --------------------------------------------
            # MONTAR DICIONÁRIO DE PERMISSÕES
            # --------------------------------------------

            usuario_dados = {}

            for indice, (campo, _nome) in enumerate(
                PERMISSOES,
                start=7
            ):

                usuario_dados[campo] = (
                    linha[indice]
                )

            usuario_html = escape(
                str(usuario)
            )

            cargo_html = escape(
                str(cargo or "-")
            )

            email_html = escape(
                str(email or "-")
            )

            empresa_html = escape(
                str(nome_empresa or "-")
            )

            plano_html = escape(
                str(plano or "basico")
            )

            # =================================================
            # STATUS ONLINE
            # =================================================

            if online:

                status_online = """
                <span class="status online">
                    ● Online
                </span>
                """

            else:

                status_online = """
                <span class="status offline">
                    ● Offline
                </span>
                """

            # =================================================
            # STATUS DA CONTA
            # =================================================

            if ativo:

                status_conta = """
                <span class="conta ativa">
                    Ativo
                </span>
                """

            else:

                status_conta = """
                <span class="conta inativa">
                    Inativo
                </span>
                """

            # =================================================
            # CARGO
            # =================================================

            if cargo == "admin":

                cargo_badge = """
                <span class="cargo admin">
                    👑 Administrador
                </span>
                """

            else:

                cargo_badge = """
                <span class="cargo operador">
                    👤 Operador
                </span>
                """

            # =================================================
            # PERMISSÕES RESUMIDAS
            # =================================================

            if cargo == "admin":

                permissao_html = """
                <span class="permissao-total">
                    🔓 Acesso total
                </span>
                """

            else:

                quantidade = sum(
                    1
                    for campo, _nome in PERMISSOES
                    if usuario_dados.get(campo)
                )

                if quantidade:

                    permissao_html = f"""
                    <span class="permissao-resumo">
                        🔐 {quantidade}/{len(PERMISSOES)}
                    </span>
                    """

                else:

                    permissao_html = """
                    <span class="sem-permissao">
                        Nenhuma
                    </span>
                    """

            # =================================================
            # ADMIN PROTEGIDO
            # =================================================

            if usuario == "admin":

                acoes_html = """
                <div class="protegido">
                    🔒 Conta administrativa protegida
                </div>
                """

            else:

                # =================================================
                # ROTAS
                # =================================================

                url_senha = url_for(
                    "usuarios_bp.alterar_senha",
                    usuario=usuario
                )

                url_plano = url_for(
                    "usuarios_bp.mudar_plano",
                    usuario=usuario
                )

                url_alternar = url_for(
                    "usuarios_bp.alternar_usuario",
                    usuario=usuario
                )

                url_permissoes = url_for(
                    "usuarios_bp.alterar_permissoes",
                    usuario=usuario
                )

                url_excluir = url_for(
                    "usuarios_bp.excluir_usuario",
                    usuario=usuario
                )

                if ativo:

                    classe_status = "vermelho"

                    texto_status = (
                        "🔴 Desativar usuário"
                    )

                else:

                    classe_status = "verde"

                    texto_status = (
                        "🟢 Ativar usuário"
                    )

                permissoes_edicao = (
                    gerar_permissoes_edicao(
                        usuario_dados
                    )
                )

                # =================================================
                # AÇÕES
                # =================================================

                acoes_html = f"""

                <div class="acoes">

                    <details class="menu">

                        <summary>
                            ⚙️ Gerenciar
                        </summary>

                        <div class="menu-conteudo">

                            <form
                                action="{url_senha}"
                                method="POST"
                            >

                                <label>
                                    Nova senha
                                </label>

                                <input
                                    type="password"
                                    name="senha"
                                    placeholder="Nova senha"
                                    minlength="4"
                                    required
                                >

                                <button
                                    class="btn azul"
                                    type="submit"
                                >
                                    🔑 Alterar senha
                                </button>

                            </form>


                            <form
                                action="{url_plano}"
                                method="POST"
                            >

                                <label>
                                    Plano
                                </label>

                                <select name="plano">

                                    <option
                                        value="basico"
                                        {"selected" if plano == "basico" else ""}
                                    >
                                        Básico
                                    </option>

                                    <option
                                        value="profissional"
                                        {"selected" if plano == "profissional" else ""}
                                    >
                                        Profissional
                                    </option>

                                    <option
                                        value="premium"
                                        {"selected" if plano == "premium" else ""}
                                    >
                                        Premium
                                    </option>

                                </select>

                                <button
                                    class="btn azul"
                                    type="submit"
                                >
                                    💎 Salvar plano
                                </button>

                            </form>


                            <form
                                action="{url_alternar}"
                                method="POST"
                            >

                                <button
                                    class="btn {classe_status}"
                                    type="submit"
                                >
                                    {texto_status}
                                </button>

                            </form>


                            <form
                                action="{url_excluir}"
                                method="POST"
                                onsubmit="return confirm('Tem certeza que deseja excluir este usuário?');"
                            >

                                <button
                                    class="btn vermelho"
                                    type="submit"
                                >
                                    🗑️ Excluir usuário
                                </button>

                            </form>

                        </div>

                    </details>


                    <details class="menu">

                        <summary>
                            🔐 Permissões ({quantidade if cargo != "admin" else "TOTAL"})
                        </summary>

                        <form
                            action="{url_permissoes}"
                            method="POST"
                            class="permissoes-edicao"
                        >

                            {permissoes_edicao}

                            <button
                                class="btn azul"
                                type="submit"
                            >
                                💾 Salvar todas as permissões
                            </button>

                        </form>

                    </details>

                </div>

                """

            # =================================================
            # LINHA DA TABELA
            # =================================================

            tabela += f"""

            <tr>

                <td>

                    <div class="usuario-nome">

                        <strong>
                            {usuario_html}
                        </strong>

                        {status_conta}

                    </div>

                </td>

                <td>
                    {cargo_badge}
                </td>

                <td>
                    {email_html}
                </td>

                <td>
                    {empresa_html}
                </td>

                <td>

                    <span class="plano {plano_html}">
                        {plano_html.capitalize()}
                    </span>

                </td>

                <td>
                    {status_online}
                </td>

                <td>
                    {permissao_html}
                </td>

                <td>
                    {acoes_html}
                </td>

            </tr>

            """

        # ====================================================
        # HTML DAS PERMISSÕES DE CRIAÇÃO
        # ====================================================

        permissoes_criacao = (
            gerar_permissoes_criacao()
        )

        # ====================================================
        # HTML
        # ====================================================

        html = f"""

<style>

.usuarios-page {{
    width:100%;
    max-width:1450px;
    margin:auto;
    padding:5px 0 30px;
}}

.usuarios-titulo {{
    margin-bottom:18px;
}}

.usuarios-titulo h2 {{
    margin:0;
    color:#fff;
    font-size:25px;
}}

.usuarios-titulo p {{
    margin:5px 0 0;
    color:#64748b;
    font-size:13px;
}}

.usuarios-box {{
    background:linear-gradient(145deg,#090909,#111);
    border:1px solid #292929;
    border-radius:14px;
    padding:20px;
    margin-bottom:20px;
    box-shadow:0 10px 30px rgba(0,0,0,.2);
}}

.usuarios-box h3 {{
    margin:0 0 18px;
    color:#fff;
    font-size:16px;
}}

.mensagem {{
    margin-top:15px;
    padding:11px 14px;
    border-radius:8px;
    font-size:13px;
    font-weight:600;
}}

.mensagem.sucesso {{
    color:#86efac;
    background:rgba(34,197,94,.08);
    border:1px solid rgba(34,197,94,.20);
}}

.mensagem.erro {{
    color:#fca5a5;
    background:rgba(239,68,68,.08);
    border:1px solid rgba(239,68,68,.20);
}}

.criar-grid {{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:12px;
}}

.campo {{
    display:flex;
    flex-direction:column;
    gap:6px;
}}

.campo label {{
    color:#94a3b8;
    font-size:11px;
    font-weight:600;
}}

.campo input,
.campo select {{
    width:100%;
    box-sizing:border-box;
    padding:11px 12px;
    border-radius:8px;
    border:1px solid #303030;
    background:#0b0b0b;
    color:#fff;
    outline:none;
}}

.campo input:focus,
.campo select:focus {{
    border-color:#3b82f6;
}}

.permissoes-box {{
    grid-column:span 2;
    padding:15px;
    border-radius:10px;
    background:#080808;
    border:1px solid #252525;
}}

.permissoes-titulo {{
    color:#fff;
    font-size:13px;
    font-weight:700;
    margin-bottom:15px;
}}

.grupo-permissoes {{
    margin-bottom:15px;
}}

.grupo-titulo {{
    color:#60a5fa;
    font-size:11px;
    font-weight:800;
    padding:8px 10px;
    background:#101010;
    border:1px solid #252525;
    border-radius:7px 7px 0 0;
}}

.grupo-grid {{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:7px;
    padding:8px;
    background:#090909;
    border:1px solid #252525;
    border-top:none;
    border-radius:0 0 7px 7px;
}}

.permissao-item {{
    display:flex;
    align-items:center;
    gap:7px;
    padding:9px;
    border-radius:7px;
    background:#111;
    border:1px solid #242424;
    color:#cbd5e1;
    font-size:11px;
    cursor:pointer;
}}

.permissao-item:hover {{
    border-color:#3b82f6;
    color:#fff;
}}

.permissao-item input,
.permissao-edicao-item input {{
    accent-color:#3b82f6;
}}

.botao-criar {{
    grid-column:span 2;
    padding:12px;
    border:none;
    border-radius:8px;
    background:#2563eb;
    color:#fff;
    font-weight:700;
    cursor:pointer;
}}

.botao-criar:hover {{
    background:#3b82f6;
}}

.tabela-container {{
    width:100%;
    overflow-x:auto;
}}

.tabela-usuarios {{
    width:100%;
    border-collapse:collapse;
    min-width:1200px;
}}

.tabela-usuarios th {{
    padding:12px;
    text-align:left;
    background:#111;
    color:#94a3b8;
    font-size:11px;
    text-transform:uppercase;
    letter-spacing:.5px;
    border-bottom:1px solid #292929;
}}

.tabela-usuarios td {{
    padding:12px;
    color:#cbd5e1;
    border-bottom:1px solid #202020;
    vertical-align:middle;
    font-size:12px;
}}

.tabela-usuarios tr:hover td {{
    background:rgba(255,255,255,.015);
}}

.usuario-nome {{
    display:flex;
    flex-direction:column;
    gap:5px;
}}

.usuario-nome strong {{
    color:#fff;
    font-size:13px;
}}

.status,
.conta,
.cargo,
.plano {{
    display:inline-flex;
    align-items:center;
    padding:4px 8px;
    border-radius:6px;
    font-size:10px;
    font-weight:700;
    white-space:nowrap;
}}

.status.online {{
    background:#16a34a;
    color:#fff;
}}

.status.offline {{
    background:#ef4444;
    color:#fff;
}}

.conta.ativa {{
    color:#86efac;
    background:rgba(34,197,94,.08);
}}

.conta.inativa {{
    color:#fca5a5;
    background:rgba(239,68,68,.08);
}}

.cargo.admin {{
    color:#facc15;
    background:rgba(250,204,21,.08);
}}

.cargo.operador {{
    color:#93c5fd;
    background:rgba(59,130,246,.08);
}}

.plano.basico {{
    color:#94a3b8;
}}

.plano.profissional {{
    color:#60a5fa;
}}

.plano.premium {{
    color:#c084fc;
}}

.permissao-total {{
    color:#22c55e;
    font-weight:700;
}}

.permissao-resumo {{
    color:#60a5fa;
    font-size:12px;
    font-weight:700;
}}

.sem-permissao {{
    color:#64748b;
}}

.acoes {{
    display:flex;
    flex-direction:column;
    gap:7px;
    min-width:190px;
}}

.menu summary {{
    list-style:none;
    cursor:pointer;
    padding:8px 10px;
    border-radius:7px;
    background:#171717;
    border:1px solid #303030;
    color:#cbd5e1;
    font-size:11px;
    font-weight:700;
}}

.menu summary:hover {{
    border-color:#3b82f6;
    color:#fff;
}}

.menu summary::-webkit-details-marker {{
    display:none;
}}

.menu-conteudo,
.permissoes-edicao {{
    margin-top:7px;
    padding:10px;
    background:#080808;
    border:1px solid #252525;
    border-radius:8px;
    display:flex;
    flex-direction:column;
    gap:8px;
}}

.menu-conteudo form {{
    display:flex;
    flex-direction:column;
    gap:5px;
}}

.menu-conteudo label {{
    color:#94a3b8;
    font-size:10px;
    font-weight:600;
}}

.menu-conteudo input,
.menu-conteudo select {{
    width:100%;
    box-sizing:border-box;
    padding:8px;
    background:#111;
    color:#fff;
    border:1px solid #303030;
    border-radius:6px;
    font-size:11px;
}}

.grupo-edicao {{
    padding:7px;
    border:1px solid #202020;
    border-radius:7px;
    background:#0c0c0c;
}}

.grupo-edicao-titulo {{
    color:#60a5fa;
    font-size:10px;
    font-weight:800;
    margin-bottom:5px;
}}

.permissao-edicao-item {{
    display:flex;
    align-items:center;
    gap:6px;
    padding:5px;
    color:#cbd5e1;
    font-size:10px;
    border-radius:5px;
    cursor:pointer;
}}

.permissao-edicao-item:hover {{
    background:#111;
    color:#fff;
}}

.btn {{
    width:100%;
    padding:8px 10px;
    border:none;
    border-radius:6px;
    color:#fff;
    font-size:10px;
    font-weight:700;
    cursor:pointer;
}}

.btn.azul {{
    background:#2563eb;
}}

.btn.azul:hover {{
    background:#3b82f6;
}}

.btn.verde {{
    background:#16a34a;
}}

.btn.vermelho {{
    background:#dc2626;
}}

.protegido {{
    color:#64748b;
    font-size:11px;
    white-space:nowrap;
}}

@media(max-width:1100px) {{

    .grupo-grid {{
        grid-template-columns:repeat(3,1fr);
    }}

}}

@media(max-width:900px) {{

    .criar-grid {{
        grid-template-columns:1fr;
    }}

    .permissoes-box,
    .botao-criar {{
        grid-column:span 1;
    }}

    .grupo-grid {{
        grid-template-columns:repeat(2,1fr);
    }}

}}

@media(max-width:600px) {{

    .grupo-grid {{
        grid-template-columns:1fr;
    }}

}}

</style>


<div class="usuarios-page">

    <div class="usuarios-titulo">

        <h2>
            👤 Usuários
        </h2>

        <p>
            Crie contas, defina permissões e controle o acesso ao sistema.
        </p>

    </div>


    <div class="usuarios-box">

        <h3>
            ➕ Criar novo usuário
        </h3>

        <form
            method="POST"
            class="criar-grid"
        >

            <div class="campo">

                <label>
                    Nome de usuário
                </label>

                <input
                    type="text"
                    name="user"
                    placeholder="Ex.: joao"
                    autocomplete="off"
                    required
                >

            </div>


            <div class="campo">

                <label>
                    Senha
                </label>

                <input
                    type="password"
                    name="senha"
                    placeholder="Senha do usuário"
                    minlength="4"
                    required
                >

            </div>


            <div class="campo">

                <label>
                    E-mail
                </label>

                <input
                    type="email"
                    name="email"
                    placeholder="usuario@email.com"
                >

            </div>


            <div class="campo">

                <label>
                    Empresa
                </label>

                <input
                    type="text"
                    name="nome_empresa"
                    placeholder="Nome da empresa"
                >

            </div>


            <div class="campo">

                <label>
                    Cargo
                </label>

                <select name="cargo">

                    <option value="operador">
                        👤 Operador
                    </option>

                    <option value="admin">
                        👑 Administrador
                    </option>

                </select>

            </div>


            <div class="campo">

                <label>
                    Plano
                </label>

                <select name="plano">

                    <option value="basico">
                        Básico
                    </option>

                    <option value="profissional">
                        Profissional
                    </option>

                    <option value="premium">
                        Premium
                    </option>

                </select>

            </div>


            <div class="permissoes-box">

                <div class="permissoes-titulo">

                    🔐 Permissões do operador

                    <span
                        style="
                            color:#64748b;
                            font-weight:normal;
                        "
                    >
                        — Administrador recebe acesso total automaticamente.
                    </span>

                </div>

                {permissoes_criacao}

            </div>


            <button
                type="submit"
                class="botao-criar"
            >
                ➕ Criar usuário
            </button>

        </form>


        {
            f'<div class="mensagem {tipo_mensagem}">{escape(mensagem)}</div>'
            if mensagem
            else ''
        }

    </div>


    <div class="usuarios-box">

        <h3>
            👥 Usuários cadastrados
        </h3>


        <div class="tabela-container">

            <table class="tabela-usuarios">

                <thead>

                    <tr>

                        <th>Usuário</th>
                        <th>Cargo</th>
                        <th>E-mail</th>
                        <th>Empresa</th>
                        <th>Plano</th>
                        <th>Login</th>
                        <th>Permissões</th>
                        <th>Ações</th>

                    </tr>

                </thead>

                <tbody>

                    {tabela}

                </tbody>

            </table>

        </div>

    </div>

</div>

"""

        return container(html)

    finally:

        try:
            devolver_conexao(conn)

        except Exception:
            pass


# ============================================================
# ALTERAR SENHA
# ============================================================

@usuarios_bp.route(
    "/usuarios/alterar_senha/<usuario>",
    methods=["POST"],
    endpoint="alterar_senha"
)
def alterar_senha(usuario):

    if not usuario_eh_admin():
        return acesso_negado()

    if usuario == "admin":
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    senha = request.form.get(
        "senha",
        ""
    ).strip()

    if not senha or len(senha) < 4:
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    conn = conectar()

    if conn is None:
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE usuarios
            SET senha = %s
            WHERE usuario = %s
            """,
            (
                generate_password_hash(senha),
                usuario
            )
        )

        conn.commit()

        try:

            registrar_log(
                session.get(
                    "user",
                    "admin"
                ),
                f"Alterou a senha do usuário {usuario}"
            )

        except Exception:
            pass

    except Exception:

        conn.rollback()

    finally:

        devolver_conexao(conn)

    return redirect(
        url_for("usuarios_bp.usuarios")
    )


# ============================================================
# ALTERAR PLANO
# ============================================================

@usuarios_bp.route(
    "/usuarios/mudar_plano/<usuario>",
    methods=["POST"],
    endpoint="mudar_plano"
)
def mudar_plano(usuario):

    if not usuario_eh_admin():
        return acesso_negado()

    if usuario == "admin":
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    plano = request.form.get(
        "plano",
        "basico"
    ).strip().lower()

    if plano not in (
        "basico",
        "profissional",
        "premium"
    ):
        plano = "basico"

    conn = conectar()

    if conn is None:
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE usuarios
            SET plano = %s
            WHERE usuario = %s
            """,
            (
                plano,
                usuario
            )
        )

        conn.commit()

    except Exception:

        conn.rollback()

    finally:

        devolver_conexao(conn)

    return redirect(
        url_for("usuarios_bp.usuarios")
    )


# ============================================================
# ATIVAR / DESATIVAR USUÁRIO
# ============================================================

@usuarios_bp.route(
    "/usuarios/alternar/<usuario>",
    methods=["POST"],
    endpoint="alternar_usuario"
)
def alternar_usuario(usuario):

    if not usuario_eh_admin():
        return acesso_negado()

    if usuario == "admin":
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    conn = conectar()

    if conn is None:
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT ativo
            FROM usuarios
            WHERE usuario = %s
            """,
            (usuario,)
        )

        resultado = cursor.fetchone()

        if resultado:

            ativo_atual = resultado[0]

            novo_status = (
                0
                if ativo_atual
                else 1
            )

            cursor.execute(
                """
                UPDATE usuarios
                SET ativo = %s
                WHERE usuario = %s
                """,
                (
                    novo_status,
                    usuario
                )
            )

            conn.commit()

            try:

                registrar_log(
                    session.get(
                        "user",
                        "admin"
                    ),
                    f"Alterou status do usuário {usuario}"
                )

            except Exception:
                pass

    except Exception:

        conn.rollback()

    finally:

        devolver_conexao(conn)

    return redirect(
        url_for("usuarios_bp.usuarios")
    )


# ============================================================
# ALTERAR PERMISSÕES
# ============================================================

@usuarios_bp.route(
    "/usuarios/permissoes/<usuario>",
    methods=["POST"],
    endpoint="alterar_permissoes"
)
def alterar_permissoes(usuario):

    if not usuario_eh_admin():
        return acesso_negado()

    if usuario == "admin":
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    permissoes = (
        pegar_permissoes_formulario()
    )

    conn = conectar()

    if conn is None:
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    cursor = conn.cursor()

    try:

        campos_update = ", ".join(
            f"{campo} = %s"
            for campo, _nome in PERMISSOES
        )

        valores = [
            permissoes[campo]
            for campo, _nome in PERMISSOES
        ]

        valores.append(usuario)

        cursor.execute(
            f"""
            UPDATE usuarios
            SET
                {campos_update}
            WHERE usuario = %s
            """,
            tuple(valores)
        )

        conn.commit()

        try:

            registrar_log(
                session.get(
                    "user",
                    "admin"
                ),
                f"Alterou permissões do usuário {usuario}"
            )

        except Exception:
            pass

    except Exception:

        conn.rollback()

    finally:

        devolver_conexao(conn)

    return redirect(
        url_for("usuarios_bp.usuarios")
    )


# ============================================================
# EXCLUIR USUÁRIO
# ============================================================

@usuarios_bp.route(
    "/usuarios/excluir_usuario/<usuario>",
    methods=["POST"],
    endpoint="excluir_usuario"
)
def excluir_usuario(usuario):

    if not usuario_eh_admin():
        return acesso_negado()

    if usuario == "admin":
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    conn = conectar()

    if conn is None:
        return redirect(
            url_for("usuarios_bp.usuarios")
        )

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM usuarios
            WHERE usuario = %s
            """,
            (usuario,)
        )

        conn.commit()

        try:

            registrar_log(
                session.get(
                    "user",
                    "admin"
                ),
                f"Excluiu o usuário {usuario}"
            )

        except Exception:
            pass

    except Exception:

        conn.rollback()

    finally:

        devolver_conexao(conn)

    return redirect(
        url_for("usuarios_bp.usuarios")
    )
