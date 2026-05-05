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

    if origem and destino:
        try:
            geo_url = "https://nominatim.openstreetmap.org/search"

            o = requests.get(geo_url, params={"q": origem, "format": "json"}).json()
            d = requests.get(geo_url, params={"q": destino, "format": "json"}).json()

            if o and d:
                origem_coord = [float(o[0]["lat"]), float(o[0]["lon"])]
                destino_coord = [float(d[0]["lat"]), float(d[0]["lon"])]

                rota_url = f"http://router.project-osrm.org/route/v1/driving/{origem_coord[1]},{origem_coord[0]};{destino_coord[1]},{destino_coord[0]}?overview=full&geometries=geojson"

                rota = requests.get(rota_url).json()

                coords = rota["routes"][0]["geometry"]["coordinates"]
        except:
            pass

    return container(f"""
        <h2>🗺️ Rotas (Grátis)</h2>

        <form method="POST">
            <input name="origem" placeholder="📍 Origem" value="{origem}">
            <input name="destino" placeholder="🏁 Destino" value="{destino}">
            <button>🚀 Calcular</button>
        </form>

        <div id="mapa" style="height:500px;"></div>

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
            var polyline = L.polyline(latlngs, {{color: 'blue'}}).addTo(map);
            map.fitBounds(polyline.getBounds());
        }}
        </script>
    """)
