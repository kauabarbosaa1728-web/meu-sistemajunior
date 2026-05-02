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

        # TOTAL
        cursor.execute(f"""
            SELECT COALESCE(SUM(valor),0)
            FROM manutencoes m
            {filtro}
        """, params)
        total_geral = float(cursor.fetchone()[0])

        # VEÍCULOS
        cursor.execute("SELECT COUNT(*) FROM veiculos")
        total_veiculos = cursor.fetchone()[0]

        media = (total_geral / (total_veiculos or 1))
        custo_km = media

        # GASTOS POR VEÍCULO
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

        top_placas = placas[:10]
        top_valores = valores[:10]

        pior_placas = placas[-10:]
        pior_valores = valores[-10:]

        # MENSAL
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

        # SELECT
        cursor.execute("SELECT id, placa FROM veiculos")
        veiculos = cursor.fetchall()

        opcoes = "<option value=''>Todos</option>"
        for v in veiculos:
            selected = "selected" if str(v[0]) == str(veiculo_id) else ""
            opcoes += f"<option value='{v[0]}' {selected}>{v[1]}</option>"

        meta = 3000

        return container(f"""

<!-- FLATPICKR -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/pt.js"></script>

<div class="dashboard">

    <div class="sidebar">
        <h3>Filtros</h3>
        <form method="GET">
            <label>Veículo</label>
            <select name="veiculo_id">{opcoes}</select>

            <label>Data início</label>
            <input type="text" id="inicio" name="inicio" placeholder="Selecione">

            <label>Data fim</label>
            <input type="text" id="fim" name="fim" placeholder="Selecione">

            <button>Filtrar</button>
        </form>
    </div>

    <div class="main">

        <h2>📊 Top 10 Piores e Melhores</h2>

        <div class="kpis">
            <div class="kpi"><span>Média</span><h2>{media:,.2f}</h2></div>
            <div class="kpi"><span>Custo KM</span><h2>R$ {custo_km:,.2f}</h2></div>
            <div class="kpi"><span>Total</span><h2>R$ {total_geral:,.2f}</h2></div>
            <div class="kpi"><span>Veículos</span><h2>{total_veiculos}</h2></div>
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
flatpickr("#inicio", {{ locale: "pt", dateFormat: "Y-m-d" }});
flatpickr("#fim", {{ locale: "pt", dateFormat: "Y-m-d" }});

const metaLine = (arr) => Array(arr.length).fill({meta});

new Chart(document.getElementById('melhores'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(top_placas)},
        datasets: [
            {{ data: {json.dumps(top_valores)}, backgroundColor: '#22c55e' }},
            {{ type:'line', data: metaLine({json.dumps(top_placas)}), borderColor:'#ef4444', fill:false }}
        ]
    }},
    options: {{ maintainAspectRatio:false }}
}});

new Chart(document.getElementById('piores'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(pior_placas)},
        datasets: [
            {{ data: {json.dumps(pior_valores)}, backgroundColor: '#22c55e' }},
            {{ type:'line', data: metaLine({json.dumps(pior_placas)}), borderColor:'#ef4444', fill:false }}
        ]
    }},
    options: {{ maintainAspectRatio:false }}
}});

new Chart(document.getElementById('mensal'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(meses)},
        datasets: [{{ data: {json.dumps(valores_mensais)}, backgroundColor:'#22c55e' }}]
    }},
    options: {{ maintainAspectRatio:false }}
}});
</script>

<style>
.dashboard {{
    display:flex;
    gap:20px;
    max-width:1400px;
    margin:auto;
    padding:20px;
}}

.sidebar {{
    width:240px;
    background:#020617;
    padding:20px;
    border-radius:12px;
}}

.main {{
    flex:1;
}}

.kpis {{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:15px;
}}

.kpi {{
    background:#111827;
    padding:20px;
    border-radius:12px;
    text-align:center;
}}

.graficos {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
    margin-top:20px;
}}

.card {{
    background:#111827;
    padding:20px;
    border-radius:12px;
    display:flex;
    flex-direction:column;
    align-items:center;
}}

.full {{
    grid-column:span 2;
}}

canvas {{
    width:100% !important;
    aspect-ratio:1/1;
    max-height:350px;
}}
</style>

        """)

    except Exception as e:
        return container(f"<pre>{str(e)}</pre>")

    finally:
        cursor.close()
        devolver_conexao(conn)
