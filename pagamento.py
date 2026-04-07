from flask import Blueprint, request, session, redirect
import mercadopago
from banco import conectar, devolver_conexao
from datetime import datetime, timedelta

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

                <button style="width:100%;padding:15px;background:#00ff00;border:none;font-size:18px;cursor:pointer;">
                    🔥 Gerar PIX
                </button>
            </form>

        </div>
    </body>
    """


# ================= CRIAR PAGAMENTO =================
@pagamento_routes.route("/criar_pagamento", methods=["GET", "POST"])
def criar_pagamento():

    # 🔥 evita erro 405
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

        if not pagamento or "response" not in pagamento:
            return "❌ erro ao gerar pagamento"

        resposta = pagamento.get("response", {})

        if "id" not in resposta:
            return f"<pre>{resposta}</pre>"

        pagamento_id = resposta["id"]

        # ================= BANCO =================
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()

            # 🔥 verifica se usuario existe
            cursor.execute("SELECT usuario FROM usuarios WHERE usuario=%s", (usuario,))
            existe = cursor.fetchone()

            if not existe:
                cursor.execute("""
                INSERT INTO usuarios (usuario, senha, email, nome_empresa, cargo, ativo)
                VALUES (%s, %s, %s, %s, 'operador', 0)
                """, (usuario, "temp", "temp@email.com", "Empresa"))

                conn.commit()

            vencimento = datetime.now() + timedelta(days=30)

            # 🔥 INSERT SIMPLES (SEM ON CONFLICT)
            cursor.execute("""
            INSERT INTO pagamentos (usuario, plano, status, pagamento_id, vencimento)
            VALUES (%s,%s,'pendente',%s,%s)
            """, (usuario, plano, pagamento_id, vencimento))

            conn.commit()

        finally:
            if conn:
                devolver_conexao(conn)

        session["pagamento_id"] = pagamento_id

        qr = resposta.get("point_of_interaction", {}).get("transaction_data", {})

        return f"""
        <body style="margin:0;background:#000;color:#fff;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
            <div style="width:420px;background:#0a0a0a;padding:30px;border-radius:10px;text-align:center;">
                
                <h2>💳 Pagamento PIX</h2>
                <p>Plano: {plano}</p>
                <p>Valor: R$ {valor}</p>

                <img src="data:image/png;base64,{qr.get("qr_code_base64","")}" style="width:220px;margin:20px 0;">

                <textarea id="pix" style="width:100%;height:100px;background:#111;color:#fff;">
{qr.get("qr_code","")}
                </textarea>

                <button onclick="copiar()" style="margin-top:10px;padding:10px;background:#00ff00;border:none;">
                    📋 Copiar PIX
                </button>

                <h3 id="status">⏳ Aguardando pagamento...</h3>

                <script>
                function copiar() {{
                    let pix = document.getElementById("pix");
                    pix.select();
                    document.execCommand("copy");
                    alert("PIX copiado!");
                }}

                async function verificar() {{
                    let r = await fetch("/verificar_pagamento_auto");
                    let t = await r.text();

                    if (t.includes("APROVADO")) {{
                        document.getElementById("status").innerHTML = "✅ PAGAMENTO APROVADO!";
                        setTimeout(() => window.location.href="/painel", 2000);
                    }}
                }}

                setInterval(verificar, 3000);
                </script>

            </div>
        </body>
        """

    except Exception as e:
        print("ERRO:", e)
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
            conn = None
            try:
                conn = conectar()
                cursor = conn.cursor()

                vencimento = datetime.now() + timedelta(days=30)

                cursor.execute("""
                UPDATE pagamentos 
                SET status='pago', data=NOW(), vencimento=%s
                WHERE pagamento_id=%s
                """, (vencimento, pagamento_id))

                cursor.execute("""
                UPDATE usuarios SET ativo=1
                WHERE usuario = (
                    SELECT usuario FROM pagamentos WHERE pagamento_id=%s
                )
                """, (pagamento_id,))

                conn.commit()
            finally:
                if conn:
                    devolver_conexao(conn)

            return "APROVADO"

        return "aguardando"

    except Exception as e:
        print("Erro verificar:", e)
        return "erro"
