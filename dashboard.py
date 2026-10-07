from flask import Blueprint, session, redirect, request, jsonify
from banco import conectar, devolver_conexao
from layout import container
from dashboard_view import render_dashboard

dashboard_bp = Blueprint("dashboard_bp", __name__)


# ============================================================
# FUNÇÃO QUE BUSCA OS DADOS DO DASHBOARD
# ============================================================
def obter_dados_dashboard(data_inicio=None, data_fim=None):

    conn = conectar()

    if conn is None:
        return None

    cursor = conn.cursor()

    try:

        filtro = ""
        valores_filtro = ()

        if data_inicio and data_fim:
            filtro = "WHERE DATE(data) BETWEEN %s AND %s"
            valores_filtro = (data_inicio, data_fim)

        # ====================================================
        # KPI
        # ====================================================

        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(quantidade), 0)
            FROM estoque
        """)
        total_qtd = cursor.fetchone()[0]

        cursor.execute(
            f"SELECT COUNT(*) FROM transferencias {filtro}",
            valores_filtro
        )
        total_transferencias = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE online=1
        """)
        usuarios_online = cursor.fetchone()[0]

        # ====================================================
        # CATEGORIAS
        # ====================================================

        cursor.execute("""
            SELECT
                COALESCE(categoria, 'Sem categoria'),
                SUM(quantidade)
            FROM estoque
            GROUP BY categoria
        """)

        categorias = cursor.fetchall()

        nomes = [c[0] for c in categorias]
        valores = [c[1] for c in categorias]

        # ====================================================
        # TOP PRODUTOS
        # ====================================================

        cursor.execute(
            f"""
            SELECT
                COALESCE(produto, 'Sem nome'),
                SUM(quantidade)
            FROM transferencias
            {filtro}
            GROUP BY produto
            ORDER BY SUM(quantidade) DESC
            LIMIT 5
            """,
            valores_filtro
        )

        top = cursor.fetchall()

        top_nomes = [t[0] for t in top]
        top_valores = [t[1] for t in top]

        # ====================================================
        # GRÁFICO DE DIAS
        # ====================================================

        cursor.execute(
            f"""
            SELECT
                DATE(data),
                COUNT(*)
            FROM transferencias
            {filtro}
            GROUP BY DATE(data)
            ORDER BY DATE(data)
            """,
            valores_filtro
        )

        dias = cursor.fetchall()

        dias_labels = [str(d[0]) for d in dias]
        dias_valores = [d[1] for d in dias]

        # ====================================================
        # ESTOQUE BAIXO
        # ====================================================

        cursor.execute("""
            SELECT produto, quantidade
            FROM estoque
            WHERE quantidade < 10
            ORDER BY quantidade ASC
            LIMIT 5
        """)

        baixo = cursor.fetchall()

        baixo_nomes = [b[0] for b in baixo]
        baixo_valores = [b[1] for b in baixo]

        # ====================================================
        # CALENDÁRIO
        # ====================================================

        cursor.execute(
            f"""
            SELECT
                DATE(data),
                COUNT(*)
            FROM transferencias
            {filtro}
            GROUP BY DATE(data)
            ORDER BY DATE(data)
            """,
            valores_filtro
        )

        dados_cal = cursor.fetchall()

        calendario = {}

        for data, total in dados_cal:

            calendario[str(data)] = {
                "entrada": total,
                "saida": 0,
                "transf": 0,
                "total": total
            }

        # ====================================================
        # RETORNO
        # ====================================================

        return {
            "total_produtos": total_produtos,
            "total_qtd": total_qtd,
            "total_transferencias": total_transferencias,
            "usuarios_online": usuarios_online,

            "nomes": nomes,
            "valores": valores,

            "top_nomes": top_nomes,
            "top_valores": top_valores,

            "dias_labels": dias_labels,
            "dias_valores": dias_valores,

            "baixo_nomes": baixo_nomes,
            "baixo_valores": baixo_valores,

            "calendario": calendario
        }

    finally:
        devolver_conexao(conn)


# ============================================================
# DASHBOARD NORMAL
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

        dados["nomes"],
        dados["valores"],

        dados["top_nomes"],
        dados["top_valores"],

        dados["dias_labels"],
        dados["dias_valores"],

        dados["baixo_nomes"],
        dados["baixo_valores"],

        dados["calendario"]
    )

    return container(html)


# ============================================================
# 🔥 NOVA ROTA
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
