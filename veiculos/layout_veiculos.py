from flask import session
from banco import conectar, devolver_conexao

# 🔥 PERMISSÃO
def tem_permissao(nome):
    if session.get("cargo") == "admin":
        return True
    return session.get(nome) == 1


def container(conteudo):

    # 🔥 ALERTA DE PROBLEMAS
    alerta = 0
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM problemas WHERE status='aberto'")
        resultado = cursor.fetchone()
        if resultado:
            alerta = resultado[0]
        cursor.close()
        devolver_conexao(conn)
    except:
        alerta = 0

    return f"""
    <html>
    <head>
        <title>KBS AUTO</title>
        <link rel="manifest" href="/static/manifest.json">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                background: linear-gradient(135deg, #0b0f19, #020617);
                color: #e5e7eb;
                font-family: Arial;
                margin: 0;
            }}

            h1 {{
                color: #3b82f6;
                text-align: center;
                margin: 10px 0;
            }}

            h2 {{
                color: #60a5fa;
                text-align: center;
            }}

            .topo {{
                background: #020617;
                padding: 15px;
                border-bottom: 1px solid #1f2937;
                position: sticky;
                top: 0;
                z-index: 1000;
            }}

            .menu {{
                display: flex;
                justify-content: center;
                gap: 10px;
                padding: 10px;
                flex-wrap: wrap;
                background: #020617;
                border-bottom: 1px solid #1f2937;
            }}

            .menu a {{
                background: #1e3a8a;
                padding: 10px 14px;
                border-radius: 8px;
                color: white;
                text-decoration: none;
                font-weight: bold;
                transition: 0.2s;
                position: relative;
            }}

            .menu a:hover {{
                background: #2563eb;
                transform: scale(1.05);
            }}

            /* 🔴 ALERTA */
            .badge {{
                background: red;
                color: white;
                border-radius: 50%;
                padding: 4px 8px;
                font-size: 12px;
                position: absolute;
                top: -8px;
                right: -8px;
            }}

            .conteudo {{
                max-width: 1100px;
                margin: auto;
                padding: 20px;
            }}

            .card {{
                background: #111827;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #1f2937;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
                margin-bottom: 20px;
            }}

            input, select, textarea {{
                width: 100%;
                padding: 10px;
                margin: 6px 0;
                background: #020617;
                color: #e5e7eb;
                border: 1px solid #3b82f6;
                border-radius: 6px;
            }}

            button {{
                width: 100%;
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                margin-top: 10px;
                cursor: pointer;
            }}

            button:hover {{
                background: #2563eb;
            }}

            img {{
                max-width: 100%;
                border-radius: 8px;
            }}
        </style>
    </head>

    <body>

        <div id="splash" style="
            position:fixed;
            top:0;
            left:0;
            width:100%;
            height:100%;
            background:#0b0f19;
            display:flex;
            align-items:center;
            justify-content:center;
            flex-direction:column;
            z-index:9999;
        ">
            <h1>🚗 KBS AUTO</h1>
            <p>Carregando...</p>
        </div>

        <div class="topo">
            <h1>🚗 KBSISTEMAS AUTO</h1>
        </div>

        <div class="menu">

            {"<a href='/veiculos'>🚗 Veículos</a>" if tem_permissao("pode_veiculos") else ""}
            {"<a href='/manutencoes'>🔧 Manutenções</a>" if tem_permissao("pode_manutencoes") else ""}
            {"<a href='/dashboard-veiculos'>📊 Dashboard</a>" if tem_permissao("pode_dashboard") else ""}

            <a href="/problemas">⚠️ Problemas</a>

            <a href="/problemas-lista">
                📋 Ocorrências
                {"<span class='badge'>" + str(alerta) + "</span>" if alerta > 0 else ""}
            </a>

        </div>

        <div class="conteudo">
            {conteudo}
        </div>

        <script>
        window.addEventListener("load", () => {{
            setTimeout(() => {{
                const splash = document.getElementById("splash");
                if (splash) splash.style.display = "none";
            }}, 500);
        }});
        </script>

    </body>
    </html>
    """
