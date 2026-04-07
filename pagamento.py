from flask import Blueprint, request, session, redirect
import mercadopago
from banco import conectar, devolver_conexao
from datetime import datetime, timedelta

pagamento_routes = Blueprint("pagamento", __name__)

sdk = mercadopago.SDK("APP_USR-6569039713831543-033108-32073b03704b3b93eac080da1fe1d0f7-1249023990")


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
        return redirect("/")

    return f"""
    <body style="background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial;">
        <div style="background:#0a0a0a;padding:30px;border-radius:10px;width:400px;text-align:center;">
            
            <h2>💰 Escolha seu plano</h2>

            <form method="POST" action="/criar_pagamento">
                <input type="hidden" name="user" value="{session['user']}">

                <select name="plano" style="width:100%;padding:10px;margin:10px 0;background:#111;color:#fff;">
                    <option value="basico">Básico - R$39,90</option>
                    <option value="profissional">Profissional - R$79,90</option>
                    <option value="premium">Premium - R$129,90</option>
                </select>

                <button style="width:100%;padding:15px;background:#00ff00;border:none;font-size:18px;">
                    🔥 Gerar PIX
                </button>
            </form>

        </div>
    </body>
    """


# ================= CRIAR PAGAMENTO =================
@pagamento_routes.route("/criar_pagamento", methods=["GET", "POST"])
def criar_pagamento():

    if request.method == "GET":
        return redirect("/pagar")

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
                "email": "cliente@email.com",
                "first_name": usuario
            }
        }

        pagamento = sdk.payment().create(payment_data)
        resposta = pagamento["response"]

        pagamento_id = resposta["id"]

        conn = conectar()
        cursor = conn.cursor()

        # 🔥 BUSCAR DADOS DO USUARIO
        cursor.execute("""
        SELECT email, nome_empresa FROM usuarios WHERE usuario=%s
        """, (usuario,))
        dados = cursor.fetchone()

        if not dados:
            # cria usuario minimo
            email = "temp@email.com"
            nome_empresa = "Empresa"

            cursor.execute("""
            INSERT INTO usuarios (usuario, senha, email, nome_empresa, cargo, ativo)
            VALUES (%s, %s, %s, %s, 'operador', 0)
            """, (usuario, "temp", email, nome_empresa))
        else:
            email = dados[0]
            nome_empresa = dados[1]

        vencimento = datetime.now() + timedelta(days=30)

        # 🔥 INSERT COMPLETO (AGORA SEM ERRO)
        cursor.execute("""
        INSERT INTO pagamentos (usuario, email, nome_empresa, plano, status, pagamento_id, vencimento)
        VALUES (%s,%s,%s,%s,'pendente',%s,%s)
        """, (usuario, email, nome_empresa, plano, pagamento_id, vencimento))

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

    except Exception as e:
        return f"❌ ERRO: {str(e)}"
