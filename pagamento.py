from flask import Blueprint, request, session
import mercadopago
from banco import conectar, devolver_conexao
from werkzeug.security import generate_password_hash

pagamento_routes = Blueprint("pagamento", __name__)

sdk = mercadopago.SDK("APP_USR-6569039713831543-033108-32073b03704b3b93eac080da1fe1d0f7-1249023990")


# ================= VALORES =================
def valor_plano(plano):
    return {
        "basico": 39.90,
        "profissional": 79.90,
        "premium": 129.90
    }.get(plano, 39.90)


# ================= PAGAR =================
@pagamento_routes.route("/pagar")
def pagar():
    if "user" not in session:
        return "Faça login"

    return f"""
    <body style="background:#000;color:#d1d5db;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
        <div style="background:#0a0a0a;padding:30px;border-radius:14px;border:1px solid #2a2a2a;text-align:center;width:400px;">
            
            <h2>💰 Regularizar pagamento</h2>

            <form method="POST" action="/criar_pagamento">
                <input type="hidden" name="user" value="{session['user']}">

                <select name="plano" style="width:100%;padding:10px;margin:10px 0;background:#111;color:#fff;">
                    <option value="basico">Básico - R$39,90</option>
                    <option value="profissional">Profissional - R$79,90</option>
                    <option value="premium">Premium - R$129,90</option>
                </select>

                <button style="width:100%;padding:15px;background:#00ff00;border:none;font-size:18px;cursor:pointer;">
                    🔥 Gerar PIX
                </button>
            </form>

        </div>
    </body>
    """


# ================= CRIAR PAGAMENTO =================
@pagamento_routes.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():
    try:
        usuario = request.form.get("user")
        plano = request.form.get("plano")

        if not usuario or not plano:
            return "❌ Dados incompletos"

        valor = valor_plano(plano)

        payment_data = {
            "transaction_amount": float(valor),
            "description": f"Plano {plano}",
            "payment_method_id": "pix",
            "payer": {
                "email": "teste@email.com",
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
        INSERT INTO pagamentos (usuario, plano, status, pagamento_id)
        VALUES (%s,%s,'pendente',%s)
        """, (usuario, plano, pagamento_id))

        conn.commit()
        devolver_conexao(conn)

        session["pagamento_id"] = pagamento_id

        qr = resposta.get("point_of_interaction", {}).get("transaction_data", {})

        return f"""
        <body style="margin:0;background:#000;color:#d1d5db;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
        
            <div style="width:420px;background:#0a0a0a;padding:30px;border-radius:14px;border:1px solid #2a2a2a;text-align:center;">
                
                <h2>Pagamento PIX</h2>
                <p>Plano: {plano}</p>
                <p>Valor: R$ {valor}</p>

                <img src="data:image/png;base64,{qr.get("qr_code_base64", "")}" style="width:220px;margin:20px 0;">

                <textarea style="width:100%;background:#111;color:#fff;border:1px solid #333;padding:10px;">
{qr.get("qr_code", "")}
                </textarea>

                <h3 id="status">⏳ Aguardando pagamento...</h3>

                <script>
                async function verificar() {{
                    const res = await fetch('/verificar_pagamento_auto');
                    const txt = await res.text();

                    if (txt.includes("APROVADO")) {{
                        document.getElementById("status").innerHTML = "✅ PAGAMENTO APROVADO!";
                        setTimeout(() => window.location.href = "/", 2000);
                    }}
                }}

                setInterval(verificar, 3000);
                </script>

            </div>
        </body>
        """

    except Exception as e:
        return f"❌ ERRO: {str(e)}"


# ================= VERIFICAR PAGAMENTO =================
@pagamento_routes.route("/verificar_pagamento_auto")
def verificar_pagamento_auto():
    try:
        pagamento_id = session.get("pagamento_id")

        if not pagamento_id:
            return "erro"

        pagamento = sdk.payment().get(pagamento_id)
        status = pagamento["response"]["status"]

        if status == "approved":
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
            UPDATE pagamentos 
            SET status='pago', data=NOW()
            WHERE pagamento_id=%s
            """, (pagamento_id,))

            conn.commit()
            devolver_conexao(conn)

            return "APROVADO"

        return "aguardando"

    except:
        return "erro"
