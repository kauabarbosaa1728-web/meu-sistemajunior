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

        # 💰 TOTAL
        cursor.execute(f"""
            SELECT COALESCE(SUM(valor),0)
            FROM manutencoes m
            {filtro}
        """, params)
        total_geral = float(cursor.fetchone()[0])

        # 🚗 VEÍCULOS
        cursor.execute("SELECT COUNT(*) FROM veiculos")
        total_veiculos = cursor.fetchone()[0]

        media = (total_geral / (total_veiculos or 1))
        custo_km = media  # depois você pode melhorar

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

        # TOP E PIORES
        top_placas = placas[:10]
        top_valores = valores[:10]

        pior_placas = placas[-10:]
        pior_valores = valores[-10:]

        # 📅 MENSAL
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

        # 🚗 SELECT
        cursor.execute("SELECT id, placa FROM veiculos")
        veiculos = cursor.fetchall()

        opcoes = "<option value=''>Todos</option>"
        for v in veiculos:
            selected = "selected" if str(v[0]) == str(veiculo_id) else ""
            opcoes += f"<option value='{v[0]}' {selected}>{v[1]}</option>"

        meta = 3000  # linha vermelha

        return container(f"""

<div class="dashboard">

    <!-- SIDEBAR -->
    <div class="sidebar">
        <h3>Filtros</h3>

        <form method="GET">
            <label>Veículo</label>
            <select name="veiculo_id">{opcoes}</select>

            <label>Data início</label>
            <input type="date" name="inicio">

            <label>Data fim</label>
            <input type="date" name="fim">

            <button>Filtrar</button>
        </form>
    </div>

    <!-- MAIN -->
    <div class="main">

        <h2>Top 10 Piores e Melhores</h2>

        <div class="kpis">
            <div class="kpi">
                <span>Média</span>
                <h2>{media:,.2f}</h2>
            </div>

            <div class="kpi">
                <span>Custo por KM</span>
                <h2>R$ {custo_km:,.2f}</h2>
            </div>

            <div class="kpi">
                <span>Total</span>
                <h2>R$ {total_geral:,.2f}</h2>
            </div>

            <div class="kpi">
                <span>Veículos</span>
                <h2>{total_veiculos}</h2>
            </div>
        </div>

        <div class="graficos">

            <div class="card">
                <h3>Top 10 Melhores</h3>
                <canvas id="melhores"></canvas>
            </div>

            <div class="card">
                <h3>Top 10 Piores</h3>
                <canvas id="piores"></canvas>
            </div>

            <div class="card full">
                <h3>Gastos Mensais</h3>
                <canvas id="mensal"></canvas>
            </div>

        </div>

    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
const metaLine = (arr) => Array(arr.length).fill({meta});

new Chart(document.getElementById('melhores'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(top_placas)},
        datasets: [
            {{
                label: 'Média',
                data: {json.dumps(top_valores)},
                backgroundColor: '#22c55e'
            }},
            {{
                type: 'line',
                label: 'Meta',
                data: metaLine({json.dumps(top_placas)}),
                borderColor: '#ef4444',
                fill: false
            }}
        ]
    }}
}});

new Chart(document.getElementById('piores'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(pior_placas)},
        datasets: [
            {{
                label: 'Média',
                data: {json.dumps(pior_valores)},
                backgroundColor: '#22c55e'
            }},
            {{
                type: 'line',
                label: 'Meta',
                data: metaLine({json.dumps(pior_placas)}),
                borderColor: '#ef4444',
                fill: false
            }}
        ]
    }}
}});

new Chart(document.getElementById('mensal'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(meses)},
        datasets: [{{
            label: 'Gastos',
            data: {json.dumps(valores_mensais)},
            backgroundColor: '#22c55e'
        }}]
    }}
}});
</script>

<style>
.dashboard {{
    display: flex;
    gap: 20px;
}}

.sidebar {{
    width: 240px;
    background: #020617;
    padding: 15px;
    border-radius: 10px;
}}

.main {{
    flex: 1;
}}

.kpis {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}}

.kpi {{
    background: #111827;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}}

.kpi span {{
    font-size: 12px;
    color: #9ca3af;
}}

.kpi h2 {{
    margin-top: 5px;
}}

.graficos {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}}

.card {{
    background: #111827;
    padding: 15px;
    border-radius: 10px;
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
