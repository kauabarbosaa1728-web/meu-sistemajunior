from flask import Blueprint, request
from banco import conectar, devolver_conexao
from veiculos.layout_veiculos import container
import json

dashboard_veiculos_bp = Blueprint("dashboard_veiculos_bp", __name__)

@dashboard_veiculos_bp.route("/dashboard-veiculos", methods=["GET", "POST"])
def dashboard_veiculos():

    conn = conectar()
    cursor = conn.cursor()

    try:
        veiculo_id = request.args.get("veiculo_id")
        data_inicio = request.args.get("inicio")
        data_fim = request.args.get("fim")

        filtro = "WHERE 1=1"
        params = []

        if veiculo_id:
            filtro += " AND m.veiculo_id = %s"
            params.append(veiculo_id)

        if data_inicio:
            filtro += " AND m.data >= %s"
            params.append(data_inicio)

        if data_fim:
            filtro += " AND m.data <= %s"
            params.append(data_fim)

        # 💰 TOTAL GERAL
        cursor.execute(f"""
            SELECT COALESCE(SUM(valor),0)
            FROM manutencoes m
            {filtro}
        """, params)
        total_geral = float(cursor.fetchone()[0])

        # 🚗 GASTO POR VEÍCULO
        cursor.execute(f"""
            SELECT v.placa, COALESCE(SUM(m.valor),0)
            FROM veiculos v
            LEFT JOIN manutencoes m ON v.id = m.veiculo_id
            {filtro.replace("m.", "")}
            GROUP BY v.placa
            ORDER BY 2 DESC
        """, params)

        dados = cursor.fetchall()
        placas = [d[0] for d in dados]
        valores = [float(d[1]) for d in dados]

        # 🔝 TOP 10
        top_placas = placas[:10]
        top_valores = valores[:10]

        # 🔻 PIORES 10
        pior_placas = placas[-10:]
        pior_valores = valores[-10:]

        # 📅 GASTO MENSAL
        cursor.execute(f"""
            SELECT TO_CHAR(data, 'YYYY-MM'), COALESCE(SUM(valor),0)
            FROM manutencoes m
            {filtro}
            GROUP BY 1
            ORDER BY 1
        """, params)

        dados_mensais = cursor.fetchall()
        meses = [d[0] for d in dados_mensais]
        valores_mensais = [float(d[1]) for d in dados_mensais]

        # 🚗 TOTAL VEÍCULOS
        cursor.execute("SELECT COUNT(*) FROM veiculos")
        total_veiculos = cursor.fetchone()[0]

        # 🚗 VEÍCULOS PARA FILTRO
        cursor.execute("SELECT id, placa FROM veiculos")
        veiculos = cursor.fetchall()

        opcoes = "<option value=''>Todos</option>"
        for v in veiculos:
            selected = "selected" if str(v[0]) == str(veiculo_id) else ""
            opcoes += f"<option value='{v[0]}' {selected}>{v[1]}</option>"

        return container(f"""

        <h2 style="text-align:center;">📊 Dashboard Veículos</h2>

        <!-- FILTRO -->
        <form method="GET">
            <select name="veiculo_id">{opcoes}</select>
            <input type="date" name="inicio">
            <input type="date" name="fim">
            <button>Filtrar</button>
        </form>

        <br>

        <!-- KPIs -->
        <div class="kpis">
            <div class="kpi">
                <h3>🚗 Veículos</h3>
                <p>{total_veiculos}</p>
            </div>

            <div class="kpi">
                <h3>💰 Total</h3>
                <p>R$ {total_geral:,.2f}</p>
            </div>

            <div class="kpi">
                <h3>📊 Média</h3>
                <p>R$ {(total_geral/(total_veiculos or 1)):,.2f}</p>
            </div>
        </div>

        <!-- GRÁFICOS -->
        <div class="graficos">

            <div class="card">
                <h3>🔝 Top 10 Veículos</h3>
                <canvas id="top"></canvas>
            </div>

            <div class="card">
                <h3>🔻 Piores 10 Veículos</h3>
                <canvas id="piores"></canvas>
            </div>

            <div class="card full">
                <h3>📅 Gastos Mensais</h3>
                <canvas id="mensal"></canvas>
            </div>

        </div>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <script>

        new Chart(document.getElementById('top'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(top_placas)},
                datasets: [{{
                    label: 'Top 10',
                    data: {json.dumps(top_valores)},
                    backgroundColor: '#22c55e'
                }}]
            }}
        }});

        new Chart(document.getElementById('piores'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(pior_placas)},
                datasets: [{{
                    label: 'Piores 10',
                    data: {json.dumps(pior_valores)},
                    backgroundColor: '#ef4444'
                }}]
            }}
        }});

        new Chart(document.getElementById('mensal'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(meses)},
                datasets: [{{
                    label: 'Gastos Mensais',
                    data: {json.dumps(valores_mensais)},
                    borderColor: '#3b82f6',
                    fill: false
                }}]
            }}
        }});

        </script>

        <style>

        .kpis {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .kpi {{
            background: #111827;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}

        .kpi h3 {{
            color: #60a5fa;
        }}

        .kpi p {{
            font-size: 28px;
            font-weight: bold;
        }}

        .graficos {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .card {{
            background: #111827;
            padding: 20px;
            border-radius: 12px;
        }}

        .full {{
            grid-column: span 2;
        }}

        </style>

        """)

    except Exception as e:
        return container(f"<pre>{str(e)}</pre>")

    finally:
        cursor.close()
        devolver_conexao(conn)
