from flask import Blueprint, request, session
import mercadopago
from banco import conectar, devolver_conexao
from werkzeug.security import generate_password_hash

pagamento_routes = Blueprint("pagamento", __name__)

sdk = mercadopago.SDK("SEU_TOKEN_AQUI")  # ⚠️ coloca seu token aqui


# ================= VALORES =================
def valor_plano(plano):
    return {
        "basico": 39.90,
        "profissional": 79.90,
        "premium": 129.90
    }.get(plano, 39.90)


# ================= CRIAR PAGAMENTO =================
@pagamento_routes.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():
    try:
        usuario = request.form.get("user")
        senha_raw = request.form.get("senha")
        email = request.form.get("email")
        empresa = request.form.get("nome_empresa")
        plano = request.form.get("plano")

        if not all([usuario, senha_raw, email, empresa, plano]):
            return "❌ Dados incompletos"

        senha = generate_password_hash(senha_raw)
        valor = valor_plano(plano)

        payment_data = {
            "transaction_amount": float(valor),
            "description": f"Plano {plano}",
            "payment_method_id": "pix",
            "payer": {
                "email": email,
                "first_name": usuario
            }
        }

        pagamento = sdk.payment().create(payment_data)
        resposta = pagamento.get("response", {})

        if "id" not in resposta:
            return f"<pre>{resposta}</pre>"

        pagamento_id = resposta["id"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO pagamentos (usuario, email, senha, nome_empresa, plano, status, pagamento_id)
        VALUES (%s,%s,%s,%s,%s,'pendente',%s)
        """, (usuario, email, senha, empresa, plano, pagamento_id))

        conn.commit()
        devolver_conexao(conn)

        session["pagamento_id"] = pagamento_id

        qr = resposta.get("point_of_interaction", {}).get("transaction_data", {})

        return f"""
        <body style="margin:0;background:#000;color:#d1d5db;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
        
            <div style="width:420px;background:#0a0a0a;padding:30px;border-radius:14px;border:1px solid #2a2a2a;text-align:center;">
                
                <h2 style="color:#fff;">Pagamento PIX</h2>
                <p>Plano: {plano}</p>
                <p>Valor: R$ {valor}</p>

                <img src="data:image/png;base64,{qr.get("qr_code_base64", "")}" style="width:220px;margin:20px 0;">

                <textarea style="width:100%;background:#111;color:#fff;border:1px solid #333;padding:10px;">
{qr.get("qr_code", "erro")}
                </textarea>

                <p style="font-size:12px;">Aguardando pagamento automático...</p>

                <script>
                setInterval(() => {{
                    fetch("/verificar_pagamento")
                    .then(res => res.text())
                    .then(html => {{
                        if(html.includes("Pagamento aprovado")) {{
                            location.href = "/";
                        }}
                    }});
                }}, 5000);
                </script>

            </div>
        </body>
        """

    except Exception as e:
        return f"❌ ERRO: {str(e)}"


# ================= WEBHOOK =================
@pagamento_routes.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "data" in data and "id" in data["data"]:
            pagamento_id = data["data"]["id"]

            pagamento = sdk.payment().get(pagamento_id)
            status = pagamento["response"]["status"]

            if status == "approved":
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute("""
                SELECT usuario, senha, email, nome_empresa, plano
                FROM pagamentos
                WHERE pagamento_id=%s AND status='pendente'
                """, (pagamento_id,))

                user = cursor.fetchone()

                if user:
                    usuario, senha, email, empresa, plano = user

                    cursor.execute("""
                    INSERT INTO usuarios (
                        usuario, senha, cargo, online, ativo, email, plano, nome_empresa,
                        pode_estoque, pode_transferencia, pode_historico
                    )
                    VALUES (%s,%s,'operador',0,1,%s,%s,%s,1,1,1)
                    """, (usuario, senha, email, plano, empresa))

                    cursor.execute("""
                    UPDATE pagamentos SET status='pago'
                    WHERE pagamento_id=%s
                    """, (pagamento_id,))

                    conn.commit()

                devolver_conexao(conn)

        return "OK", 200

    except Exception as e:
        return str(e), 500


# ================= VERIFICAR =================
@pagamento_routes.route("/verificar_pagamento")
def verificar_pagamento():
    try:
        pagamento_id = session.get("pagamento_id")

        if not pagamento_id:
            return "erro"

        pagamento = sdk.payment().get(pagamento_id)
        status = pagamento["response"]["status"]

        if status == "approved":
            return "Pagamento aprovado"

        return "Aguardando"

    except:
        return "erro"


# ================= PAINEL =================
@pagamento_routes.route("/mensalidades")
def mensalidades():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT usuario, plano, status FROM pagamentos ORDER BY id DESC")
    dados = cursor.fetchall()

    html = "<h2>Mensalidades</h2><table border=1><tr><th>User</th><th>Plano</th><th>Status</th></tr>"

    for u,p,s in dados:
        html += f"<tr><td>{u}</td><td>{p}</td><td>{s}</td></tr>"

    html += "</table>"

    devolver_conexao(conn)

    return f"<body style='background:#000;color:#fff'>{html}</body>"
