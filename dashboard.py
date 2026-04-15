from flask import Blueprint, session, redirect
from banco import conectar, devolver_conexao
from layout import container
from datetime import datetime
import json

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/painel")
def painel():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    try:
        # ===== DADOS =====
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM estoque")
        total_qtd = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transferencias")
        total_transferencias = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE online=1")
        usuarios_online = cursor.fetchone()[0]

        # ===== DISTRIBUIÇÃO =====
        cursor.execute("""
        SELECT COALESCE(categoria, 'Sem categoria'), SUM(quantidade)
        FROM estoque
        GROUP BY categoria
        """)
        categorias = cursor.fetchall()
        nomes = [c[0] for c in categorias]
        valores = [c[1] for c in categorias]

        # ===== TOP PRODUTOS =====
        cursor.execute("""
        SELECT produto, SUM(quantidade)
        FROM transferencias
        GROUP BY produto
        ORDER BY SUM(quantidade) DESC
        LIMIT 5
        """)
        top = cursor.fetchall()
        top_nomes = [t[0] for t in top]
        top_valores = [t[1] for t in top]

        # ===== MOVIMENTAÇÃO =====
        cursor.execute("""
        SELECT DATE(data), COUNT(*)
        FROM transferencias
        GROUP BY DATE(data)
        ORDER BY DATE(data)
        LIMIT 7
        """)
        dias = cursor.fetchall()
        dias_labels = [str(d[0]) for d in dias]
        dias_valores = [d[1] for d in dias]

        # ===== BAIXO ESTOQUE =====
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

        # ===== DATA =====
        now = datetime.now()
        nome_mes = [
            "", "Janeiro","Fevereiro","Março","Abril","Maio",
            "Junho","Julho","Agosto","Setembro","Outubro",
            "Novembro","Dezembro"
        ][now.month]

        html = f"""
        <div class="wrap">

            <h2>🚀 Dashboard - {nome_mes}</h2>

            <!-- CARDS -->
            <div class="cards">
                <div class="card"><h1>{total_produtos}</h1><p>Produtos</p></div>
                <div class="card"><h1>{total_qtd}</h1><p>Quantidade</p></div>
                <div class="card"><h1>{total_transferencias}</h1><p>Movimentações</p></div>
                <div class="card"><h1>{usuarios_online}</h1><p>Online</p></div>
            </div>

            <!-- GRID POWER BI -->
            <div class="grid">

                <!-- PRINCIPAL -->
                <div class="box grande">
                    <h3>Distribuição Geral</h3>
                    <canvas id="pizza"></canvas>
                </div>

                <div class="box">
                    <h3>Movimentações</h3>
                    <canvas id="linha"></canvas>
                </div>

                <div class="box">
                    <h3>Top Produtos</h3>
                    <canvas id="top"></canvas>
                </div>

                <div class="box">
                    <h3>Baixo Estoque</h3>
                    <canvas id="baixo"></canvas>
                </div>

            </div>

        </div>

        <script>

        new Chart(document.getElementById('pizza'), {{
            type:'doughnut',
            data:{{labels:{json.dumps(nomes)},datasets:[{{data:{json.dumps(valores)}}}]}}
        }});

        new Chart(document.getElementById('linha'), {{
            type:'line',
            data:{{
                labels:{json.dumps(dias_labels)},
                datasets:[{{data:{json.dumps(dias_valores)},borderColor:'#22c55e',tension:0.4}}]
            }}
        }});

        new Chart(document.getElementById('top'), {{
            type:'bar',
            data:{{
                labels:{json.dumps(top_nomes)},
                datasets:[{{data:{json.dumps(top_valores)},backgroundColor:'#3b82f6'}}]
            }}
        }});

        new Chart(document.getElementById('baixo'), {{
            type:'bar',
            data:{{
                labels:{json.dumps(baixo_nomes)},
                datasets:[{{data:{json.dumps(baixo_valores)},backgroundColor:'#ef4444'}}]
            }}
        }});

        </script>

        <style>

        .wrap {{
            max-width: 1200px;
            margin: auto;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(4,1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}

        .card {{
            background: #0b0b0b;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 0 10px #3b82f640;
        }}

        /* POWER BI GRID */
        .grid {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            grid-template-rows: auto auto;
            gap: 20px;
        }}

        .box {{
            background: #0b0b0b;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 0 10px #3b82f640;
        }}

        .grande {{
            grid-column: 1 / 2;
            grid-row: 1 / 3;
        }}

        canvas {{
            width: 100% !important;
            height: 300px !important;
        }}

        @media(max-width:768px){{
            .cards{{grid-template-columns:1fr 1fr}}
            .grid{{grid-template-columns:1fr}}
            .grande{{grid-column:auto;grid-row:auto}}
        }}

        </style>
        """

        return container(html)

    finally:
        devolver_conexao(conn)
