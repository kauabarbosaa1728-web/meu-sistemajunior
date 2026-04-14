def container(c):
    return f"""
    <html>
    <head>
        <title>KBSISTEMAS</title>
        <link rel="icon" type="image/png" href="/static/logo.png">
        <link rel="shortcut icon" href="/static/logo.png">
        <meta http-equiv="Cache-Control" content="public, max-age=300">

        <style>

        body {{
            margin: 0;
            font-family: monospace;
            background: #000000;
            color: #d1d5db;
        }}

        .logo-text {{
            font-size: 18px;
            color: #e5e7eb;
            font-weight: bold;
            letter-spacing: 1px;
        }}

        .menu {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .menu a {{
            margin-right: 0;
            padding: 8px 12px;
            border-radius: 10px;
            transition: 0.2s;
            border: 1px solid transparent;
            color: #cfcfcf;
        }}

        .menu a:hover {{
            background: #1a1a1a;
            color: #ffffff;
            text-decoration: none;
            border-color: #3a3a3a;
        }}

        .logout {{
            color: #f87171 !important;
            border: 1px solid #4a2020 !important;
        }}

        .logout:hover {{
            background: #2a1111 !important;
            color: #ffb4b4 !important;
            border-color: #6a2a2a !important;
        }}

        .overlay {{
            padding: 20px;
            min-height: 100vh;
            background: #000000;
        }}

        a {{
            color: #d1d5db;
            text-decoration: none;
            margin-right: 15px;
        }}

        a:hover {{
            color: #ffffff;
            text-decoration: underline;
        }}

        input, button, select, textarea {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            border: 1px solid #3a3a3a;
            background: #111111;
            color: #e5e7eb;
            font-family: monospace;
        }}

        textarea {{
            width: 100%;
            min-height: 80px;
        }}

        input[type="checkbox"] {{
            width: auto;
            transform: scale(1.1);
            margin-right: 8px;
        }}

        button {{
            cursor: pointer;
            transition: 0.2s;
            background: #161616;
        }}

        button:hover {{
            background: #2a2a2a;
            color: #ffffff;
            border-color: #5a5a5a;
            font-weight: bold;
        }}

        table {{
            width: 100%;
            background: #0d0d0d;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            padding: 10px;
            border: 1px solid #2f2f2f;
            text-align: left;
            vertical-align: top;
        }}

        th {{
            background: #151515;
            color: #f3f4f6;
        }}

        .card {{
            background: #0b0b0b;
            border: 1px solid #2c2c2c;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 20px;
            color: #e5e7eb;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .mini-card {{
            background: linear-gradient(180deg, #121212 0%, #070707 100%);
            border: 1px solid #3a3a3a;
            border-radius: 14px;
            padding: 20px;
            color: #e5e7eb;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }}

        .mensagem {{ margin-top:10px; font-weight:bold; }}
        .erro {{ color:#f87171; }}
        .sucesso {{ color:#86efac; }}

        .btn-danger {{ color:#f87171; border-color:#7f1d1d; }}
        .btn-danger:hover {{ background:#2a1111; color:#fff; }}

        .btn-warning {{ color:#facc15; border-color:#5a4a12; }}
        .btn-warning:hover {{ background:#2a2410; color:#fff; }}

        .btn-edit {{
            color:#d1d5db;
            border:1px solid #4a4a4a;
            padding:6px 10px;
            border-radius:8px;
        }}

        .btn-edit:hover {{
            background:#1f1f1f;
            color:#fff;
        }}

        .permissoes-box {{
            display:grid;
            grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
            gap:8px;
            margin-top:10px;
        }}

        .perm-item {{
            background:#111;
            padding:8px;
            border-radius:8px;
            border:1px solid #2f2f2f;
        }}

        </style>
    </head>

    <body>
        {topo()}

        <div class="page-loader" id="pageLoader"></div>

        <div class="overlay" id="mainContent">
            {c}
        </div>

    </body>
    </html>
    """
