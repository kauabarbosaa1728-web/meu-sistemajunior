from flask import Blueprint, request, redirect
import mercadopago
from banco import conectar, devolver_conexao

pagamento_routes = Blueprint("pagamento", __name__)

sdk = mercadopago.SDK("APP_USR-6569039713831543-033108-32073b03704b3b93eac080da1fe1d0f7-1249023990")

def valor_plano(plano):
    if plano == "basico":
        return 39.90
    elif plano == "profissional":
        return 79.90
    elif plano == "premium":
        return 129.90
    return 0

@pagamento_routes.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():
    usuario = request.form["user"]
    senha = request.form["senha"]
    email = request.form["email"]
    empresa = request.form["nome_empresa"]
    plano = request.form["plano"]

    valor = valor_plano(plano)

    preference_data = {
        "items": [
            {
                "title": f"Plano {plano}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": valor
            }
        ],
        "back_urls": {
            "success": "http://localhost:5000/sucesso",
            "failure": "http://localhost:5000/erro",
            "pending": "http://localhost:5000/pendente"
        },
        "auto_return": "approved"
    }

    preference = sdk.preference().create(preference_data)

    # salva no banco como pendente
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pagamentos (usuario, email, senha, nome_empresa, plano, status)
    VALUES (%s,%s,%s,%s,%s,'pendente')
    """, (usuario, email, senha, empresa, plano))

    conn.commit()
    devolver_conexao(conn)

    return redirect(preference["response"]["init_point"])


@pagamento_routes.route("/sucesso")
def sucesso():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT usuario, senha, email, nome_empresa, plano
    FROM pagamentos
    WHERE status='pendente'
    ORDER BY id DESC LIMIT 1
    """)

    user = cursor.fetchone()

    if user:
        usuario, senha, email, empresa, plano = user

        cursor.execute("""
        INSERT INTO usuarios (
            usuario, senha, cargo, online, ativo, email, plano, nome_empresa,
            pode_estoque, pode_transferencia, pode_historico,
            pode_usuarios, pode_editar_estoque, pode_excluir_estoque, pode_logs
        )
        VALUES (%s,%s,'operador',0,1,%s,%s,%s,1,0,1,0,0,0,0)
        """, (usuario, senha, email, plano, empresa))

        cursor.execute("UPDATE pagamentos SET status='pago' WHERE usuario=%s", (usuario,))
        conn.commit()

    devolver_conexao(conn)

    return "✅ Pagamento aprovado! Agora você pode fazer login."
