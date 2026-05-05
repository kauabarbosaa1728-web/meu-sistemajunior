from flask import Blueprint, request, redirect, session
from layout import container

from .repository import (
    buscar_estoque_completo,
    inserir_produto,
    buscar_estoque_baixo,
    buscar_produto_por_id,
    atualizar_produto,
    excluir_produto,
    listar_produtos_transferencia,
    listar_usuarios_transferencia,
    fazer_transferencia,
    buscar_historico_transferencias,
    buscar_logs,
    criar_tabela_entradas,
    inserir_entrada,
    buscar_historico_entradas,

    # NOVOS
    criar_tabela_categorias,
    listar_categorias,
    inserir_categoria,

    criar_tabela_fornecedores,
    listar_fornecedores,
    inserir_fornecedor,

    criar_tabela_ncm,
    inserir_ncm
)

from .service import (
    validar_usuario_logado,
    verificar_bloqueio,
    verificar_bloqueio_simples,
    verificar_permissao_estoque,
    verificar_permissao_excluir,
    calcular_totais,
    registrar_add_estoque,
    registrar_edicao_estoque,
    registrar_exclusao_estoque,
    registrar_transferencia,
    registrar_entrada_estoque,

    # NOVOS
    validar_categoria,
    validar_fornecedor,
    validar_ncm,
    registrar_categoria,
    registrar_fornecedor,
    registrar_ncm
)

# 🔥 CORRIGIDO AQUI
from .views_estoque import (
    montar_alerta_estoque_baixo,
    montar_tabela_estoque,
    render_estoque
)

from .views_operacoes import (
    render_editar_estoque,
    render_produto_nao_encontrado,
    render_erro_atualizar,
    render_transferencia,
    render_historico,
    render_entrada
)

from .exportacoes import gerar_excel_estoque, gerar_pdf_estoque


estoque_bp = Blueprint("estoque_bp", __name__)


# ================= ESTOQUE =================
@estoque_bp.route("/estoque", methods=["GET", "POST"])
def estoque():
    if not validar_usuario_logado(session):
        return redirect("/")

    liberado, aviso_ou_bloqueio = verificar_bloqueio(session)
    if not liberado:
        return aviso_ou_bloqueio

    aviso = aviso_ou_bloqueio

    permitido, resposta = verificar_permissao_estoque()
    if not permitido:
        return resposta

    msg = ""

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")
        valor = request.form.get("valor")

        if produto and qtd:
            try:
                qtd = int(qtd)
                valor = float(valor or 0)

                inserir_produto(produto, qtd, categoria, valor)
                registrar_add_estoque(session["user"], produto, qtd)

                msg = "✅ Produto adicionado com sucesso"

            except Exception as e:
                msg = f"❌ Erro: {e}"

    dados = buscar_estoque_completo()
    total_qtd, total_valor = calcular_totais(dados)

    baixo = buscar_estoque_baixo()
    alerta_html = montar_alerta_estoque_baixo(baixo)

    tabela = montar_tabela_estoque(dados)

    return container(render_estoque(
        aviso,
        alerta_html,
        total_qtd,
        total_valor,
        tabela,
        msg
    ))


# ================= EXPORTAÇÕES =================
@estoque_bp.route("/exportar_estoque")
def exportar_estoque():
    if not validar_usuario_logado(session):
        return redirect("/")
    return gerar_excel_estoque()


@estoque_bp.route("/exportar_pdf")
def exportar_pdf():
    if not validar_usuario_logado(session):
        return redirect("/")
    return gerar_pdf_estoque()


# ================= EDITAR =================
@estoque_bp.route("/editar_estoque/<int:id>", methods=["GET", "POST"])
def editar_estoque(id):
    if not validar_usuario_logado(session):
        return redirect("/")

    liberado, resposta = verificar_bloqueio_simples(session)
    if not liberado:
        return resposta

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")
        valor = request.form.get("valor")

        try:
            qtd = int(qtd)
            valor = float(valor or 0)

            atualizar_produto(id, produto, qtd, categoria, valor)
            registrar_edicao_estoque(session["user"], produto)

            return redirect("/estoque")

        except Exception as e:
            return container(render_erro_atualizar(e))

    dado = buscar_produto_por_id(id)

    if not dado:
        return container(render_produto_nao_encontrado())

    return container(render_editar_estoque(dado))


# ================= EXCLUIR =================
@estoque_bp.route("/excluir_estoque/<int:id>")
def excluir_estoque_rota(id):
    if not validar_usuario_logado(session):
        return redirect("/")

    liberado, resposta = verificar_bloqueio_simples(session)
    if not liberado:
        return resposta

    permitido, resposta = verificar_permissao_excluir()
    if not permitido:
        return resposta

    try:
        excluir_produto(id)
        registrar_exclusao_estoque(session["user"], id)
    except Exception as e:
        print("Erro ao excluir:", e)

    return redirect("/estoque")


# ================= TRANSFERENCIA =================
@estoque_bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    if not validar_usuario_logado(session):
        return redirect("/")

    msg = ""

    produtos = listar_produtos_transferencia()
    usuarios = listar_usuarios_transferencia()

    if request.method == "POST":
        produto = request.form["produto"]
        qtd = int(request.form["qtd"])
        destino = request.form.get("destino")

        sucesso, msg = fazer_transferencia(produto, qtd, destino, session["user"])

        if sucesso:
            registrar_transferencia(session["user"], produto, destino)

    historico = buscar_historico_transferencias()

    return container(render_transferencia(produtos, usuarios, historico, msg))


# ================= HISTÓRICO =================
@estoque_bp.route("/historico")
def historico():
    if not validar_usuario_logado(session):
        return redirect("/")

    busca = request.args.get("busca", "")
    dados = buscar_logs(busca)

    return container(render_historico(busca, dados))


# ================= ENTRADA =================
@estoque_bp.route("/entrada", methods=["GET", "POST"])
def entrada():
    if not validar_usuario_logado(session):
        return redirect("/")

    liberado, resposta = verificar_bloqueio_simples(session)
    if not liberado:
        return resposta

    permitido, resposta = verificar_permissao_estoque()
    if not permitido:
        return resposta

    criar_tabela_entradas()

    msg = ""

    if request.method == "POST":
        produto = request.form.get("produto")
        qtd = request.form.get("qtd")
        categoria = request.form.get("categoria")
        fornecedor = request.form.get("fornecedor")
        valor = request.form.get("valor")

        try:
            qtd = int(qtd)
            valor = float(valor or 0)

            inserir_entrada(produto, qtd, categoria, fornecedor, valor, session["user"])
            registrar_entrada_estoque(session["user"], produto)

            msg = "✅ Entrada registrada"

        except Exception as e:
            msg = f"❌ Erro: {e}"

    historico = buscar_historico_entradas()

    return container(render_entrada(msg, historico))


# ================= CATEGORIAS =================
@estoque_bp.route("/categorias", methods=["GET", "POST"])
def categorias():
    criar_tabela_categorias()
    msg = ""

    if request.method == "POST":
        nome = request.form.get("nome")

        valido, erro = validar_categoria(nome)
        if not valido:
            msg = erro
        else:
            inserir_categoria(nome)
            registrar_categoria(session["user"], nome)
            msg = "✅ Categoria cadastrada"

    lista = listar_categorias()
    html = "<h2>Categorias</h2>"

    for c in lista:
        html += f"<p>• {c}</p>"

    html += f"""
    <form method="POST">
        <input name="nome" placeholder="Nova categoria">
        <button>Salvar</button>
    </form>
    <p>{msg}</p>
    """

    return container(html)


# ================= FORNECEDORES =================
@estoque_bp.route("/fornecedores", methods=["GET", "POST"])
def fornecedores():
    criar_tabela_fornecedores()
    msg = ""

    if request.method == "POST":
        nome = request.form.get("nome")
        contato = request.form.get("contato")

        valido, erro = validar_fornecedor(nome)
        if not valido:
            msg = erro
        else:
            inserir_fornecedor(nome, contato)
            registrar_fornecedor(session["user"], nome)
            msg = "✅ Fornecedor cadastrado"

    lista = listar_fornecedores()
    html = "<h2>Fornecedores</h2>"

    for f in lista:
        html += f"<p>• {f}</p>"

    html += f"""
    <form method="POST">
        <input name="nome" placeholder="Nome">
        <input name="contato" placeholder="Contato">
        <button>Salvar</button>
    </form>
    <p>{msg}</p>
    """

    return container(html)


# ================= NCM =================
@estoque_bp.route("/ncm", methods=["GET", "POST"])
def ncm():
    criar_tabela_ncm()
    msg = ""

    if request.method == "POST":
        codigo = request.form.get("codigo")
        descricao = request.form.get("descricao")

        valido, erro = validar_ncm(codigo)
        if not valido:
            msg = erro
        else:
            inserir_ncm(codigo, descricao)
            registrar_ncm(session["user"], codigo)
            msg = "✅ NCM cadastrado"

    html = f"""
    <h2>NCM</h2>
    <form method="POST">
        <input name="codigo" placeholder="Código NCM">
        <input name="descricao" placeholder="Descrição">
        <button>Salvar</button>
    </form>
    <p>{msg}</p>
    """

    return container(html)
