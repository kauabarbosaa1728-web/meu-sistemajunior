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

        nomes = [c[0] if c[0] else "Sem categoria" for c in categorias]
        valores = [c[1] if c[1] else 0 for c in categorias]

        # ===== TOP PRODUTOS =====
        cursor.execute("""
        SELECT COALESCE(produto, 'Sem nome'), SUM(quantidade)
        FROM transferencias
        GROUP BY produto
        ORDER BY SUM(quantidade) DESC
        LIMIT 5
        """)
        top = cursor.fetchall()

        top_nomes = [t[0] if t[0] else "Sem nome" for t in top]
        top_valores = [t[1] if t[1] else 0 for t in top]

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
        dias_valores = [d[1] if d[1] else 0 for d in dias]

        # ===== BAIXO ESTOQUE =====
        cursor.execute("""
        SELECT produto, quantidade
        FROM estoque
        WHERE quantidade < 10
        ORDER BY quantidade ASC
        LIMIT 5
        """)
        baixo = cursor.fetchall()

        baixo_nomes = [b[0] if b[0] else "Sem nome" for b in baixo]
        baixo_valores = [b[1] if b[1] else 0 for b in baixo]

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

            <!-- KPI -->
            <div class="cards">
                <div class="card"><h1>{total_produtos}</h1><p>Total Produtos</p></div>
                <div class="card"><h1>{total_qtd}</h1><p>Quantidade</p></div>
                <div class="card"><h1>{total_transferencias}</h1><p>Movimentações</p></div>
                <div class="card"><h1>{usuarios_online}</h1><p>Online</p></div>
            </div>

            <!-- GRÁFICOS -->
            <div class="grid">

                <div class="box">
                    <h3>📊 Distribuição</h3>
                    <canvas id="pizza"></canvas>
                </div>

                <div class="box">
                    <h3>📈 Movimentações</h3>
                    <canvas id="linha"></canvas>
                </div>

                <div class="box">
                    <h3>🔥 Top Produtos</h3>
                    <canvas id="top"></canvas>
                </div>

                <div class="box">
                    <h3>⚠️ Baixo Estoque</h3>
                    <canvas id="baixo"></canvas>
                </div>

            </div>

        </div>

        <script>

        const cores = ["#00ff9c","#00bfff","#ffaa00","#ff4d4d","#a855f7"];

        // 📊 DISTRIBUIÇÃO
        new Chart(document.getElementById('pizza'), {{
            type:'doughnut',
            data:{{
                labels:{json.dumps(nomes)},
                datasets:[{{
                    data:{json.dumps(valores)},
                    backgroundColor:cores,
                    borderWidth:2
                }}]
            }},
            options:{{
                cutout:'65%',
                plugins:{{legend:{{labels:{{color:"#ccc"}}}}}}
            }}
        }});

        // 📈 MOVIMENTAÇÃO
        new Chart(document.getElementById('linha'), {{
            type:'line',
            data:{{
                labels:{json.dumps(dias_labels)},
                datasets:[{{
                    label:"Movimentações",
                    data:{json.dumps(dias_valores)},
                    borderColor:"#00ff9c",
                    tension:0.4
                }}]
            }},
            options:{{
                plugins:{{legend:{{labels:{{color:"#ccc"}}}}}},
                scales:{{
                    x:{{ticks:{{color:"#aaa"}}}},
                    y:{{ticks:{{color:"#aaa"}}}}
                }}
            }}
        }});

        // 🔥 TOP
        new Chart(document.getElementById('top'), {{
            type:'bar',
            data:{{
                labels:{json.dumps(top_nomes)},
                datasets:[{{
                    data:{json.dumps(top_valores)},
                    backgroundColor:"#00bfff",
                    borderRadius:8
                }}]
            }},
            options:{{
                plugins:{{legend:{{display:false}}}},
                scales:{{
                    x:{{ticks:{{color:"#aaa"}}}},
                    y:{{ticks:{{color:"#aaa"}}}}
                }}
            }}
        }});

        // ⚠️ BAIXO
        new Chart(document.getElementById('baixo'), {{
            type:'bar',
            data:{{
                labels:{json.dumps(baixo_nomes)},
                datasets:[{{
                    data:{json.dumps(baixo_valores)},
                    backgroundColor:"#ff4d4d",
                    borderRadius:8
                }}]
            }},
            options:{{
                plugins:{{legend:{{display:false}}}},
                scales:{{
                    x:{{ticks:{{color:"#aaa"}}}},
                    y:{{ticks:{{color:"#aaa"}}}}
                }}
            }}
        }});

        </script>

        <style>
        .wrap{{max-width:1200px;margin:auto}}

        .cards{{
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:15px;
            margin-bottom:20px
        }}

        .card{{
            background:linear-gradient(145deg,#0a0f1a,#05070d);
            padding:20px;
            border-radius:15px;
            text-align:center;
            box-shadow:0 0 20px rgba(0,255,150,0.1);
        }}

        .card h1{{font-size:28px;color:#00ff9c}}

        .grid{{
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:20px
        }}

        .box{{
            background:#0b0f1a;
            padding:15px;
            border-radius:15px;
            box-shadow:0 0 20px rgba(0,255,150,0.05)
        }}

        canvas{{
            width:100%!important;
            height:250px!important
        }}

        @media(max-width:768px){{
            .cards{{grid-template-columns:1fr 1fr}}
            .grid{{grid-template-columns:1fr}}
        }}
        </style>
        """

        return container(html)

    finally:
        devolver_conexao(conn)
