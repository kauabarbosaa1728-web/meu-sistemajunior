from flask import Blueprint, request, session, redirect
import mercadopago
from banco import conectar, devolver_conexao
from datetime import datetime, timedelta

pagamento_routes = Blueprint("pagamento", __name__)

sdk = mercadopago.SDK("APP_USR-6569039713831543-033108-32073b03704b3b93eac080da1fe1d0f7-1249023990")


# ================= PAGAR =================
@pagamento_routes.route("/pagar")
def pagar():
    if "user" not in session:
        return redirect("/")

    return f"""
    <body style="background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial;">
        <div style="background:#0a0a0a;padding:30px;border-radius:10px;width:400px;text-align:center;">
            
            <h2>Escolha seu plano</h2>

            <form method="POST" action="/gerar_pix">
                <select name="plano" style="width:100%;padding:10px;margin:10px 0;background:#111;color:#fff;">
                    <option value="basico">Básico - R$39,90</option>
                    <option value="profissional">Profissional - R$79,90</option>
                    <option value="premium">Premium - R$129,90</option>
                </select>

                <button style="width:100%;padding:15px;background:#00ff00;border:none;">
                    Gerar PIX
                </button>
            </form>

        </div>
    </body>
    """


# ================= GERAR PIX =================
@pagamento_routes.route("/gerar_pix", methods=["POST"])
def gerar_pix():
    usuario = session.get("user")
    plano = request.form.get("plano")

    valores = {
        "basico": 39.90,
        "profissional": 79.90,
        "premium": 129.90
    }

    valor = valores.get(plano, 39.90)

    payment_data = {
        "transaction_amount": float(valor),
        "description": f"Plano {plano}",
        "payment_method_id": "pix",
        "payer": {
            "email": "cliente@email.com"
        }
    }

    pagamento = sdk.payment().create(payment_data)
    resposta = pagamento["response"]

    pagamento_id = resposta["id"]

    conn = conectar()
    cursor = conn.cursor()

    vencimento = datetime.now() + timedelta(days=30)

    # 🔥 SALVA PAGAMENTO LIMPO
    cursor.execute("""
    INSERT INTO pagamentos (usuario, plano, status, pagamento_id, vencimento)
    VALUES (%s,%s,'pendente',%s,%s)
    """, (usuario, plano, pagamento_id, vencimento))

    conn.commit()
    devolver_conexao(conn)

    session["pagamento_id"] = pagamento_id

    qr = resposta["point_of_interaction"]["transaction_data"]

    return f"""
    <body style="background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial;">
        <div style="background:#0a0a0a;padding:30px;border-radius:10px;width:400px;text-align:center;">
            
            <h2>💳 Pagamento PIX</h2>

            <img src="data:image/png;base64,{qr["qr_code_base64"]}" style="width:220px;margin:20px;">

            <textarea id="pix" style="width:100%;height:100px;background:#111;color:#fff;">
{qr["qr_code"]}
            </textarea>

            <button onclick="copiar()" style="margin-top:10px;padding:10px;background:#00ff00;">
                Copiar PIX
            </button>

            <h3 id="status">Aguardando pagamento...</h3>

            <script>
            function copiar() {{
                let pix = document.getElementById("pix");
                pix.select();
                document.execCommand("copy");
                alert("Copiado!");
            }}

            async function verificar() {{
                let r = await fetch("/verificar_pagamento_auto");
                let t = await r.text();

                if (t.includes("APROVADO")) {{
                    document.getElementById("status").innerHTML = "PAGO!";
                    setTimeout(() => window.location.href="/painel", 2000);
                }}
            }}

            setInterval(verificar, 3000);
            </script>

        </div>
    </body>
    """
