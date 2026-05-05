from flask import Blueprint, request, redirect, session
from layout import container

rotas_bp = Blueprint("rotas_bp", __name__)

@rotas_bp.route("/rotas", methods=["GET", "POST"])
def rotas():

    if "user" not in session:
        return redirect("/")

    origem = request.form.get("origem") if request.method == "POST" else ""
    destino = request.form.get("destino") if request.method == "POST" else ""

    return container(f"""
        <h2>🗺️ Rotas (GPS)</h2>

        <form method="POST">
            <input name="origem" placeholder="📍 Origem" value="{origem}">
            <input name="destino" placeholder="🏁 Destino" value="{destino}">
            <button>🚀 Calcular Rota</button>
        </form>

        <div id="info-rota" style="margin:10px 0; font-size:18px;"></div>

        <div id="mapa" style="width:100%; height:500px; border-radius:12px;"></div>

        <!-- 🔥 GOOGLE MAPS -->
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBqiPS7ZDcxqptaYxoGJW8QAes3tEeuE0A"></script>

        <script>
        function iniciarMapa() {{

            var mapa = new google.maps.Map(document.getElementById("mapa"), {{
                zoom: 7,
                center: {{ lat: -23.55, lng: -46.63 }},

                // 🔥 CONTROLES
                streetViewControl: true,
                mapTypeControl: true,
                fullscreenControl: true,
                zoomControl: true
            }});

            var directionsService = new google.maps.DirectionsService();
            var directionsRenderer = new google.maps.DirectionsRenderer();

            directionsRenderer.setMap(mapa);

            var origem = "{origem}";
            var destino = "{destino}";

            if(origem && destino) {{

                var request = {{
                    origin: origem,
                    destination: destino,
                    travelMode: "DRIVING"
                }};

                directionsService.route(request, function(result, status) {{

                    if (status == "OK") {{

                        directionsRenderer.setDirections(result);

                        let tempo = result.routes[0].legs[0].duration.text;
                        let distancia = result.routes[0].legs[0].distance.text;

                        document.getElementById("info-rota").innerHTML =
                            "⏱ Tempo: " + tempo + " | 📏 Distância: " + distancia;

                    }} else {{
                        document.getElementById("info-rota").innerHTML =
                            "❌ Não foi possível calcular a rota";
                    }}
                }});
            }}
        }}

        window.onload = iniciarMapa;
        </script>
    """)
