from banco import verificar_pagamento, registrar_log
from layout import acesso_negado
from permissoes import tem_permissao


# ================= USUÁRIO =================

def validar_usuario_logado(session):
    return "user" in session


# ================= BLOQUEIO SAAS =================

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


# ================= PERMISSÕES =================

def verificar_permissao_estoque():
    if not tem_permissao("pode_estoque"):
        return False, acesso_negado()
    return True, ""


def verificar_permissao_excluir():
    if not tem_permissao("pode_excluir_estoque"):
        return False, acesso_negado()
    return True, ""


# ================= CÁLCULOS =================

def calcular_totais(dados):
    total_qtd = sum(d[2] for d in dados)
    total_valor = sum(d[2] * float(d[4] or 0) for d in dados)
    return total_qtd, total_valor


# ================= VALIDAÇÕES NOVAS =================

def validar_produto(produto, qtd, valor):
    if not produto:
        return False, "❌ Nome do produto obrigatório"

    if qtd is None or int(qtd) < 0:
        return False, "❌ Quantidade inválida"

    try:
        float(valor)
    except:
        return False, "❌ Valor inválido"

    return True, ""


def validar_categoria(nome):
    if not nome or len(nome) < 2:
        return False, "❌ Categoria inválida"
    return True, ""


def validar_fornecedor(nome):
    if not nome:
        return False, "❌ Nome do fornecedor obrigatório"
    return True, ""


def validar_ncm(codigo):
    if not codigo or len(codigo) < 4:
        return False, "❌ NCM inválido"
    return True, ""


# ================= LOGS =================

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


# ================= NOVOS LOGS =================

def registrar_categoria(usuario, nome):
    registrar_log(usuario, "categoria", nome)


def registrar_fornecedor(usuario, nome):
    registrar_log(usuario, "fornecedor", nome)


def registrar_ncm(usuario, codigo):
    registrar_log(usuario, "ncm", codigo)


def registrar_nota_fiscal(usuario, numero):
    registrar_log(usuario, "nota_fiscal", numero)
