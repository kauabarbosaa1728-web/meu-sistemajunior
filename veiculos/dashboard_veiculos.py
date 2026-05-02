from flask import Blueprint, request
from banco import conectar, devolver_conexao
from layout import layout
import json

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
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

        total_geral = cursor.fetchone()[0]

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

        # 📊 GASTO MENSAL
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

        # 🚗 VEÍCULOS PARA FILTRO
        cursor.execute("SELECT id, placa FROM veiculos")
        veiculos = cursor.fetchall()

        opcoes = "<option value=''>Todos</option>"
        for v in veiculos:
            selected = "selected" if str(v[0]) == str(veiculo_id) else ""
            opcoes += f"<option value='{v[0]}' {selected}>{v[1]}</option>"

        return layout(f"""
            <h2>📊 Dashboard Avançado</h2>

            <form method="GET">
                <select name="veiculo_id">
                    {opcoes}
                </select>

                <input type="date" name="inicio">
                <input type="date" name="fim">

                <button>Filtrar</button>
            </form>

            <br>

            <div style="background:#1e3a8a;padding:20px;border-radius:10px;">
                <h3>💰 Total Geral</h3>
                <h1>R$ {total_geral}</h1>
            </div>

            <br>

            <h3>🚗 Gastos por Veículo</h3>
            <canvas id="grafico1"></canvas>

            <br><br>

            <h3>📅 Gastos Mensais</h3>
            <canvas id="grafico2"></canvas>

            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

            <script>
                new Chart(document.getElementById('grafico1'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(placas)},
                        datasets: [{{
                            label: 'Gastos por Veículo',
                            data: {json.dumps(valores)},
                            backgroundColor: '#3b82f6'
                        }}]
                    }}
                }});

                new Chart(document.getElementById('grafico2'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(meses)},
                        datasets: [{{
                            label: 'Gastos Mensais',
                            data: {json.dumps(valores_mensais)},
                            borderColor: '#60a5fa',
                            fill: false
                        }}]
                    }}
                }});
            </script>
        """)

    except Exception as e:
        return layout(f"<pre>{str(e)}</pre>")

    finally:
        cursor.close()
        devolver_conexao(conn)
