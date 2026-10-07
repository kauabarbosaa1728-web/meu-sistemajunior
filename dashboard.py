from flask import Blueprint, session, redirect, request, jsonify
from banco import conectar, devolver_conexao
from layout import container
from dashboard_view import render_dashboard


dashboard_bp = Blueprint("dashboard_bp", __name__)


# ============================================================
# BUSCAR DADOS DO DASHBOARD
# ============================================================

def obter_dados_dashboard(data_inicio=None, data_fim=None):

    conn = conectar()

    if conn is None:
        return None

    cursor = conn.cursor()

    try:

        # ====================================================
        # FILTRO DE DATA
        # ====================================================

        filtro = ""
        valores_filtro = ()

        if data_inicio and data_fim:

            filtro = "WHERE DATE(data) BETWEEN %s AND %s"
            valores_filtro = (
                data_inicio,
                data_fim
            )

        # ====================================================
        # TOTAL DE PRODUTOS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM estoque
        """)

        total_produtos = cursor.fetchone()[0]

        # ====================================================
        # QUANTIDADE TOTAL
        # ====================================================

        cursor.execute("""
            SELECT COALESCE(SUM(quantidade), 0)
            FROM estoque
        """)

        total_qtd = cursor.fetchone()[0]

        # ====================================================
        # TOTAL DE TRANSFERÊNCIAS
        # ====================================================

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM transferencias
            {filtro}
            """,
            valores_filtro
        )

        total_transferencias = cursor.fetchone()[0]

        # ====================================================
        # USUÁRIOS ONLINE
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE online = 1
        """)

        usuarios_online = cursor.fetchone()[0]

        # ====================================================
        # PRODUTOS DO GRÁFICO INTELIGENTE
        #
        # Mostra os 10 produtos com maior quantidade
        # diretamente da tabela estoque.
        # ====================================================

        cursor.execute("""
            SELECT
                COALESCE(produto, 'Sem nome'),
                COALESCE(SUM(quantidade), 0)
            FROM estoque
            GROUP BY produto
            ORDER BY SUM(quantidade) DESC
            LIMIT 10
        """)

        produtos_grafico = cursor.fetchall()

        grafico_labels = [
            str(item[0])
            for item in produtos_grafico
        ]

        grafico_valores = [
            item[1]
            for item in produtos_grafico
        ]

        # ====================================================
        # ESTOQUE BAIXO
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM estoque
            WHERE quantidade < 10
        """)

        quantidade_baixo_estoque = cursor.fetchone()[0]

        # ====================================================
        # PRODUTOS COM ESTOQUE BAIXO
        # ====================================================

        cursor.execute("""
            SELECT
                COALESCE(produto, 'Sem nome'),
                quantidade
            FROM estoque
            WHERE quantidade < 10
            ORDER BY quantidade ASC
            LIMIT 10
        """)

        baixo = cursor.fetchall()

        baixo_produtos = [
            {
                "produto": str(item[0]),
                "quantidade": item[1]
            }
            for item in baixo
        ]

        # ====================================================
        # RETORNO
        # ====================================================

        return {

            "total_produtos": total_produtos,

            "total_qtd": total_qtd,

            "total_transferencias": total_transferencias,

            "usuarios_online": usuarios_online,

            "grafico_labels": grafico_labels,

            "grafico_valores": grafico_valores,

            "quantidade_baixo_estoque":
                quantidade_baixo_estoque,

            "baixo_produtos":
                baixo_produtos
        }

    finally:

        devolver_conexao(conn)


# ============================================================
# DASHBOARD
# ============================================================

@dashboard_bp.route("/painel")
def painel():

    if "user" not in session:
        return redirect("/")

    data_inicio = request.args.get("inicio")
    data_fim = request.args.get("fim")

    dados = obter_dados_dashboard(
        data_inicio,
        data_fim
    )

    if dados is None:
        return "Erro de conexão com o banco."

    html = render_dashboard(
        dados["total_produtos"],
        dados["total_qtd"],
        dados["total_transferencias"],
        dados["usuarios_online"],
        dados["grafico_labels"],
        dados["grafico_valores"],
        dados["quantidade_baixo_estoque"],
        dados["baixo_produtos"]
    )

    return container(html)


# ============================================================
# DADOS DO DASHBOARD EM TEMPO REAL
# ============================================================

@dashboard_bp.route("/painel/dados")
def painel_dados():

    if "user" not in session:

        return jsonify({
            "erro": "não autenticado"
        }), 401

    data_inicio = request.args.get("inicio")
    data_fim = request.args.get("fim")

    dados = obter_dados_dashboard(
        data_inicio,
        data_fim
    )

    if dados is None:

        return jsonify({
            "erro": "erro de conexão"
        }), 500

    return jsonify(dados)
