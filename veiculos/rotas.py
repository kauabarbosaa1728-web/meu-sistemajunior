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

    if origem and destino:
        try:
            geo_url = "https://nominatim.openstreetmap.org/search"

            o = requests.get(geo_url, params={"q": origem, "format": "json"}).json()
            d = requests.get(geo_url, params={"q": destino, "format": "json"}).json()

            if o and d:
                lat_o, lon_o = float(o[0]["lat"]), float(o[0]["lon"])
                lat_d, lon_d = float(d[0]["lat"]), float(d[0]["lon"])

                rota_url = f"http://router.project-osrm.org/route/v1/driving/{lon_o},{lat_o};{lon_d},{lat_d}?overview=full&geometries=geojson"

                rota = requests.get(rota_url).json()

                dados = rota["routes"][0]
                coords = dados["geometry"]["coordinates"]

                # 🔥 tempo e distância
                distancia_km = dados["distance"] / 1000
                tempo_min = dados["duration"] / 60

                distancia = f"{distancia_km:.1f} km"
                tempo = f"{tempo_min:.0f} min"

        except:
            pass

    return container(f"""
        <h2>🗺️ Rotas Inteligentes</h2>

        <form method="POST">
            <input name="origem" placeholder="📍 Origem" value="{origem}">
            <input name="destino" placeholder="🏁 Destino" value="{destino}">
            <button>🚀 Calcular Rota</button>
        </form>

        <div style="margin:15px 0; font-size:18px;">
            ⏱ Tempo: <b>{tempo}</b> &nbsp;&nbsp; | &nbsp;&nbsp;
            📏 Distância: <b>{distancia}</b>
        </div>

        <div id="mapa" style="height:500px; border-radius:12px;"></div>

        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

        <script>
        var map = L.map('mapa').setView([-23.55, -46.63], 7);

        L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19
        }}).addTo(map);

        var coords = {coords};

        if(coords.length > 0) {{

            var latlngs = coords.map(c => [c[1], c[0]]);

            // 🔥 linha da rota
            var polyline = L.polyline(latlngs, {{
                color: '#3b82f6',
                weight: 6
            }}).addTo(map);

            // 🔥 marcadores
            var inicio = latlngs[0];
            var fim = latlngs[latlngs.length - 1];

            L.marker(inicio).addTo(map).bindPopup("📍 Origem");
            L.marker(fim).addTo(map).bindPopup("🏁 Destino");

            // 🔥 zoom automático
            map.fitBounds(polyline.getBounds());

            // 🔥 animação simples (linha desenhando)
            var i = 0;
            var linhaAnimada = L.polyline([], {{color: '#22c55e', weight: 6}}).addTo(map);

            function animar() {{
                if(i < latlngs.length) {{
                    linhaAnimada.addLatLng(latlngs[i]);
                    i++;
                    setTimeout(animar, 5);
                }}
            }}

            animar();
        }}
        </script>
    """)
