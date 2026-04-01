from flask import Blueprint, request, session
import mercadopago
from banco import conectar, devolver_conexao
from werkzeug.security import generate_password_hash

pagamento_routes = Blueprint("pagamento", **name**)

# 🔐 TOKEN

sdk = mercadopago.SDK("APP_USR-6569039713831543-033108-32073b03704b3b93eac080da1fe1d0f7-1249023990")

# ================= VALOR DOS PLANOS =================

def valor_plano(plano):
return {
"basico": 39.90,
"profissional": 79.90,
"premium": 129.90
}.get(plano, 39.90)

# ================= CRIAR PAGAMENTO PIX =================

@pagamento_routes.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():
try:
usuario = request.form.get("user")
senha_raw = request.form.get("senha")
email = request.form.get("email")
empresa = request.form.get("nome_empresa")
plano = request.form.get("plano")

```
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

    # 🔥 CORREÇÃO DO ERRO 'id'
    if "id" not in resposta:
        return f"""
        <h2>❌ ERRO NO MERCADO PAGO</h2>
        <pre>{resposta}</pre>
        """

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
    <body style="background:black;color:#00ff00;text-align:center;padding-top:50px;">
    <h2>💰 PAGAMENTO PIX</h2>
    <p>Plano: {plano}</p>
    <p>Valor: R$ {valor}</p>

    <p>Copie o código:</p>
    <textarea rows=5 cols=60>{qr.get("qr_code", "erro")}</textarea><br><br>

    <img src="data:image/png;base64,{qr.get("qr_code_base64", "")}"><br><br>

    <a href="/verificar_pagamento">Já paguei</a>
    </body>
    """

except Exception as e:
    return f"❌ ERRO: {str(e)}"
```

# ================= VERIFICAR PAGAMENTO =================

@pagamento_routes.route("/verificar_pagamento")
def verificar_pagamento():
try:
pagamento_id = session.get("pagamento_id")

```
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
        <body style="background:black;color:#00ff00;text-align:center;padding-top:100px;">
        <h2>✅ PAGAMENTO APROVADO!</h2>
        <a href="/">Fazer login</a>
        </body>
        """

    return f"""
    <body style="background:black;color:#00ff00;text-align:center;padding-top:100px;">
    <h2>⏳ Aguardando pagamento...</h2>
    <p>Status: {status}</p>
    <a href="/verificar_pagamento">Atualizar</a>
    </body>
    """

except Exception as e:
    return f"❌ ERRO AO VERIFICAR: {str(e)}"
```
