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
            <input name="origem" placeholder="Origem" value="{origem}">
            <input name="destino" placeholder="Destino" value="{destino}">
            <button>Calcular</button>
        </form>

        <div id="mapa" style="height:400px;"></div>

        <script src="https://maps.googleapis.com/maps/api/js?key=SUA_CHAVE_AQUI"></script>

        <script>
        function init() {{

            var map = new google.maps.Map(document.getElementById("mapa"), {{
                zoom: 7,
                center: {{ lat: -23.55, lng: -46.63 }}
            }});

            var directionsService = new google.maps.DirectionsService();
            var directionsRenderer = new google.maps.DirectionsRenderer();

            directionsRenderer.setMap(map);

            var origem = "{origem}";
            var destino = "{destino}";

            if(origem && destino) {{
                directionsService.route({{
                    origin: origem,
                    destination: destino,
                    travelMode: "DRIVING"
                }}, function(result, status) {{

                    if (status === "OK") {{
                        directionsRenderer.setDirections(result);
                    }}
                }});
            }}
        }}

        window.onload = init;
        </script>
    """)
