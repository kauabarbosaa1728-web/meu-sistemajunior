from flask import Blueprint, request, redirect, session
from layout import container
import requests

rotas_bp = Blueprint("rotas_bp", __name__)

@rotas_bp.route("/rotas", methods=["GET", "POST"])
def rotas():

    if "user" not in session:
        return redirect("/")

    origem = request.form.get("origem") if request.method == "POST" else ""
    destino = request.form.get("destino") if request.method == "POST" else ""

    coords = []
    tempo = ""
    distancia = ""
    mensagem = ""

    def buscar_endereco(endereco):
        url = "https://nominatim.openstreetmap.org/search"

        headers = {
            "User-Agent": "KBSISTEMAS-Rotas/1.0"
        }

        params = {
            "q": endereco,
            "format": "json",
            "limit": 1,
            "countrycodes": "br"
        }

        resposta = requests.get(url, params=params, headers=headers, timeout=10)
        dados = resposta.json()

        if dados:
            return float(dados[0]["lat"]), float(dados[0]["lon"])

        return None

    if origem and destino:
        try:
            origem_busca = origem
            destino_busca = destino

            if "sp" not in origem.lower():
                origem_busca += ", Mauá, SP, Brasil"

            if "sp" not in destino.lower():
                destino_busca += ", Mauá, SP, Brasil"

            ponto_origem = buscar_endereco(origem_busca)
            ponto_destino = buscar_endereco(destino_busca)

            if not ponto_origem:
                mensagem = "❌ Não encontrei a origem. Tente colocar: rua, número, cidade e estado."

            elif not ponto_destino:
                mensagem = "❌ Não encontrei o destino. Tente colocar: rua, número, cidade e estado."

            else:
                lat_o, lon_o = ponto_origem
                lat_d, lon_d = ponto_destino

                rota_url = (
                    f"https://router.project-osrm.org/route/v1/driving/"
                    f"{lon_o},{lat_o};{lon_d},{lat_d}"
                    f"?overview=full&geometries=geojson"
                )

                rota = requests.get(rota_url, timeout=10).json()

                if "routes" in rota and len(rota["routes"]) > 0:
                    dados = rota["routes"][0]

                    coords = dados["geometry"]["coordinates"]

                    distancia_km = dados["distance"] / 1000
                    tempo_min = dados["duration"] / 60

                    distancia = f"{distancia_km:.1f} km"
                    tempo = f"{tempo_min:.0f} min"
                    mensagem = "✅ Rota calculada com sucesso!"

                else:
                    mensagem = "❌ Não foi possível calcular a rota entre esses endereços."

        except Exception as e:
            mensagem = f"❌ Erro ao calcular rota: {str(e)}"

    return container(f"""
        <h2>🗺️ Rotas Inteligentes</h2>

        <form method="POST">
            <input name="origem" placeholder="📍 Origem: Rua, número, cidade, estado" value="{origem}">
            <input name="destino" placeholder="🏁 Destino: Rua, número, cidade, estado" value="{destino}">
            <button>🚀 Calcular Rota</button>
        </form>

        <div style="margin:15px 0; font-size:17px;">
            <b>{mensagem}</b>
        </div>

        <div style="margin:15px 0; font-size:18px;">
            ⏱ Tempo: <b>{tempo}</b> &nbsp;&nbsp; | &nbsp;&nbsp;
            📏 Distância: <b>{distancia}</b>
        </div>

        <div id="mapa" style="height:500px; border-radius:12px;"></div>

        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

        <script>
        var map = L.map('mapa').setView([-23.667, -46.461], 13);

        L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19
        }}).addTo(map);

        var coords = {coords};

        if(coords.length > 0) {{

            var latlngs = coords.map(c => [c[1], c[0]]);

            var polyline = L.polyline(latlngs, {{
                color: '#2563eb',
                weight: 7
            }}).addTo(map);

            var inicio = latlngs[0];
            var fim = latlngs[latlngs.length - 1];

            L.marker(inicio).addTo(map).bindPopup("📍 Origem").openPopup();
            L.marker(fim).addTo(map).bindPopup("🏁 Destino");

            map.fitBounds(polyline.getBounds(), {{
                padding: [40, 40]
            }});

            var carroIcon = L.divIcon({{
                html: "🚗",
                className: "",
                iconSize: [30, 30]
            }});

            var carro = L.marker(inicio, {{icon: carroIcon}}).addTo(map);

            let i = 0;

            function moverCarro() {{
                if(i < latlngs.length) {{
                    carro.setLatLng(latlngs[i]);
                    i++;
                    setTimeout(moverCarro, 25);
                }}
            }}

            moverCarro();
        }}
        </script>
    """)
