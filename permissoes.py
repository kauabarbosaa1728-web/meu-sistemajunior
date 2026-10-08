from flask import session
from banco import conectar, devolver_conexao


# ==========================================================
# TODAS AS PERMISSÕES DO SISTEMA
# ==========================================================

PERMISSOES_SISTEMA = [

    # ==========================
    # ESTOQUE
    # ==========================
    "pode_estoque",
    "pode_transferencia",
    "pode_historico",
    "pode_editar_estoque",
    "pode_excluir_estoque",
    "pode_entrada_estoque",
    "pode_categorias",
    "pode_fornecedores",
    "pode_ncm",
    "pode_exportar_estoque",
    "pode_pdf_estoque",

    # ==========================
    # SISTEMA
    # ==========================
    "pode_usuarios",
    "pode_logs",

    # ==========================
    # FINANCEIRO
    # ==========================
    "pode_financeiro",
    "pode_entrada_financeiro",
    "pode_saida_financeiro",
    "pode_resumo_financeiro",
    "pode_relatorio_financeiro",

    # ==========================
    # VENDAS
    # ==========================
    "pode_vendas",
    "pode_historico_vendas",

    # ==========================
    # RELATÓRIOS
    # ==========================
    "pode_relatorios",
    "pode_relatorio_geral",
    "pode_relatorio_estoque",
    "pode_relatorio_veiculos",
    "pode_relatorio_problemas",

    # ==========================
    # VEÍCULOS
    # ==========================
    "pode_veiculos",
    "pode_manutencoes",
    "pode_dashboard",
    "pode_rotas",

    # ==========================
    # PROBLEMAS
    # ==========================
    "pode_problemas",
    "pode_ocorrencias",
    "pode_resolver_problemas",
    "pode_excluir_problemas",
    "pode_pdf_problemas",

    # ==========================
    # OUTROS
    # ==========================
    "pode_ia",
    "pode_configuracoes",
]


# ==========================================================
# CARREGAR PERMISSÕES DO USUÁRIO
# ==========================================================

def carregar_permissoes(usuario):
    conn = None

    try:
        conn = conectar()

        if conn is None:
            return

        cursor = conn.cursor()

        campos = ", ".join(
            ["cargo", "ativo", "email", "plano", "nome_empresa"]
            + PERMISSOES_SISTEMA
        )

        cursor.execute(
            f"""
            SELECT {campos}
            FROM usuarios
            WHERE usuario=%s
            """,
            (usuario,)
        )

        dado = cursor.fetchone()

        if not dado:
            return

        # ==================================================
        # INFORMAÇÕES BÁSICAS
        # ==================================================

        cargo = dado[0]

        session["cargo"] = cargo
        session["ativo"] = bool(dado[1])
        session["email"] = dado[2] or ""
        session["plano"] = dado[3] or ""
        session["nome_empresa"] = dado[4] or ""

        # ==================================================
        # ADMIN
        # ==================================================
        # ADMIN TEM ACESSO TOTAL INDEPENDENTEMENTE DO BANCO
        # ==================================================

        if cargo == "admin":

            for permissao in PERMISSOES_SISTEMA:
                session[permissao] = True

            return

        # ==================================================
        # USUÁRIO NORMAL
        # ==================================================

        inicio_permissoes = 5

        for i, permissao in enumerate(PERMISSOES_SISTEMA):

            valor = dado[inicio_permissoes + i]

            session[permissao] = bool(valor)

    except Exception as e:

        print("❌ Erro ao carregar permissões:", e)

    finally:

        if conn:
            devolver_conexao(conn)


# ==========================================================
# VERIFICAR PERMISSÃO
# ==========================================================

def tem_permissao(nome):

    # ADMIN SEMPRE TEM ACESSO TOTAL
    if session.get("cargo") == "admin":
        return True

    return bool(session.get(nome, False))


# ==========================================================
# VERIFICAR VÁRIAS PERMISSÕES
# ==========================================================

def tem_alguma_permissao(*nomes):

    if session.get("cargo") == "admin":
        return True

    for nome in nomes:
        if session.get(nome, False):
            return True

    return False


def tem_todas_permissoes(*nomes):

    if session.get("cargo") == "admin":
        return True

    for nome in nomes:
        if not session.get(nome, False):
            return False

    return True


# ==========================================================
# LIMPAR PERMISSÕES DA SESSÃO
# ==========================================================

def limpar_permissoes():

    for permissao in PERMISSOES_SISTEMA:
        session.pop(permissao, None)


# ==========================================================
# BARRAS 3D DO DASHBOARD
# ==========================================================

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

            <div class="bar-value">
                {valor}
            </div>

            <div class="bar-3d-wrap" style="height:{altura}px;">

                <div
                    class="bar-3d-front"
                    style="height:{altura}px; background:{cor_frente};">
                </div>

                <div
                    class="bar-3d-side"
                    style="height:{altura}px; background:{cor_lado};">
                </div>

                <div
                    class="bar-3d-top"
                    style="background:{cor_topo};">
                </div>

            </div>

            <div class="bar-label">
                {nome}
            </div>

        </div>
        """

    return barras
