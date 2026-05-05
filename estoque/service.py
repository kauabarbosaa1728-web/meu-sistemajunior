from banco import verificar_pagamento, registrar_log
from layout import acesso_negado
from permissoes import tem_permissao


def validar_usuario_logado(session):
    return "user" in session


def verificar_bloqueio(session):
    aviso = ""

    if session.get("cargo") != "admin":
        status = verificar_pagamento(session["user"])

        if status == "bloqueado":
            return False, """
            <h1 style='color:red;text-align:center;margin-top:50px;'>
            🚫 Sistema bloqueado<br><br>
            Efetue o pagamento para continuar
            </h1>
            """

        elif status == "aviso":
            aviso = "<div style='color:yellow;text-align:center;'>⚠️ Seu plano está vencendo!</div>"

    return True, aviso


def verificar_bloqueio_simples(session):
    if session.get("cargo") != "admin":
        status = verificar_pagamento(session["user"])

        if status == "bloqueado":
            return False, "<h1 style='color:red'>🚫 Sistema bloqueado</h1>"

    return True, ""


def verificar_permissao_estoque():
    if not tem_permissao("pode_estoque"):
        return False, acesso_negado()
    return True, ""


def verificar_permissao_excluir():
    if not tem_permissao("pode_excluir_estoque"):
        return False, acesso_negado()
    return True, ""


def calcular_totais(dados):
    total_qtd = sum(d[2] for d in dados)
    total_valor = sum(d[2] * float(d[4] or 0) for d in dados)
    return total_qtd, total_valor


def registrar_add_estoque(usuario, produto, qtd):
    registrar_log(usuario, "add_estoque", f"{produto} ({qtd})")


def registrar_edicao_estoque(usuario, produto):
    registrar_log(usuario, "editar_estoque", produto)


def registrar_exclusao_estoque(usuario, id):
    registrar_log(usuario, "excluir_estoque", str(id))


def registrar_transferencia(usuario, produto, destino):
    registrar_log(usuario, "transferencia", f"{produto} -> {destino}")


def registrar_entrada_estoque(usuario, produto):
    registrar_log(usuario, "entrada_estoque", produto)
