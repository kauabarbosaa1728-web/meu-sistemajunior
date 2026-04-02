from flask import Blueprint, request, session
import mercadopago
from banco import conectar, devolver_conexao
from werkzeug.security import generate_password_hash

pagamento_routes = Blueprint("pagamento", __name__)

sdk = mercadopago.SDK("APP_USR-6569039713831543-033108-32073b03704b3b93eac080da1fe1d0f7-1249023990")

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

        # 🔥 NOVA TELA BONITA
        return f"""
        <body style="margin:0;background:#000;color:#d1d5db;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;">
        
            <div style="width:420px;background:#0a0a0a;padding:30px;border-radius:14px;border:1px solid #2a2a2a;text-align:center;box-shadow:0 0 20px #000;">
                
                <h2 style="color:#ffffff;">Pagamento PIX</h2>
                <p style="color:#9ca3af;">Plano: {plano}</p>
                <p style="color:#9ca3af;">Valor: R$ {valor}</p>

                <img src="data:image/png;base64,{qr.get("qr_code_base64", "")}"
                style="width:220px;margin:20px 0;border-radius:10px;border:1px solid #333;">

                <textarea style="width:100%;background:#111;color:#fff;border:1px solid #333;padding:10px;border-radius:6px;">
{qr.get("qr_code", "erro")}
                </textarea>

                <form action="/verificar_pagamento">
                    <button style="width:100%;padding:12px;margin-top:15px;background:#1f1f1f;border:1px solid #444;color:#fff;border-radius:8px;">
                        Já paguei
                    </button>
                </form>

                <p style="margin-top:10px;color:#6b7280;font-size:12px;">
                    Após pagar, clique no botão acima
                </p>

            </div>
        </body>
        """

    except Exception as e:
        return f"❌ ERRO: {str(e)}"


# ================= VERIFICAR =================
@pagamento_routes.route("/verificar_pagamento")
def verificar_pagamento():
    try:
        pagamento_id = session.get("pagamento_id")

        if not pagamento_id:
            return "❌ Pagamento não encontrado"

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

            return """
            <body style="background:#000;color:#00ff00;text-align:center;padding-top:100px;">
            <h2>Pagamento aprovado!</h2>
            <a href="/">Entrar no sistema</a>
            </body>
            """

        return f"""
        <body style="background:#000;color:#d1d5db;text-align:center;padding-top:100px;">
        <h2>Aguardando pagamento...</h2>
        <p>Status: {status}</p>
        <a href="/verificar_pagamento">Atualizar</a>
        </body>
        """

    except Exception as e:
        return f"❌ ERRO AO VERIFICAR: {str(e)}"
