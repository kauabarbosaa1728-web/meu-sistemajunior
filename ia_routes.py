from flask import Blueprint, request, session, redirect
from banco import conectar, devolver_conexao
from tradutor import t
import difflib

ia_bp = Blueprint("ia_bp", __name__)

# ================= BUSCAR PRODUTO =================
def encontrar_produto(pergunta):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT produto FROM estoque")
    produtos = [p[0].lower() for p in cursor.fetchall()]

    devolver_conexao(conn)

    palavras = pergunta.lower().split()

    for palavra in palavras:
        resultado = difflib.get_close_matches(palavra, produtos, n=1, cutoff=0.6)
        if resultado:
            return resultado[0]

    return None


# ================= IA TURBINADA =================
def resposta_inteligente(pergunta):
    pergunta_lower = pergunta.lower()

    conn = conectar()
    cursor = conn.cursor()

    # ===== SAUDAÇÃO =====
    if any(p in pergunta_lower for p in ["oi", "ola", "eai", "fala", "hello", "hi"]):
        devolver_conexao(conn)
        return t("👋 Olá! Posso te ajudar com estoque, financeiro, veículos e relatórios.")

    # ===== AJUDA =====
    if "ajuda" in pergunta_lower or "help" in pergunta_lower:
        devolver_conexao(conn)
        return t("Você pode perguntar sobre estoque, financeiro, produtos, veículos, relatórios ou qualquer informação do sistema.")

    # ===== TOTAL ESTOQUE =====
    if any(p in pergunta_lower for p in ["quantos", "total", "estoque", "produtos", "itens"]):
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM estoque")
        qtd = cursor.fetchone()[0]

        devolver_conexao(conn)
        return t(f"📦 Você tem {total} produtos cadastrados, totalizando {qtd} itens no estoque.")

    # ===== BUSCAR PRODUTO =====
    produto = encontrar_produto(pergunta)

    if produto:
        cursor.execute(
            "SELECT produto, quantidade FROM estoque WHERE LOWER(produto)=%s",
            (produto,)
        )
        resultado = cursor.fetchone()

        devolver_conexao(conn)

        if resultado:
            return t(f"📦 O produto '{resultado[0]}' possui {resultado[1]} unidades.")

    # ===== LISTAR PRODUTOS =====
    if any(p in pergunta_lower for p in ["listar", "mostrar", "ver produtos"]):
        cursor.execute("SELECT produto, quantidade FROM estoque LIMIT 10")
        dados = cursor.fetchall()

        devolver_conexao(conn)

        if not dados:
            return t("📭 Seu estoque está vazio.")

        texto = t("📋 Produtos encontrados:") + "\n"
        for p, q in dados:
            texto += t(f"- {p}: {q}") + "\n"

        return texto

    # ===== MAIOR PRODUTO =====
    if any(p in pergunta_lower for p in ["maior", "mais", "top"]):
        cursor.execute("SELECT produto, quantidade FROM estoque ORDER BY quantidade DESC LIMIT 1")
        p = cursor.fetchone()

        devolver_conexao(conn)

        if p:
            return t(f"🏆 Produto com maior estoque: {p[0]} ({p[1]} unidades).")

    # ===== FINANCEIRO =====
    if "financeiro" in pergunta_lower:
        try:
            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada'")
            entrada = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida'")
            saida = cursor.fetchone()[0]

            saldo = entrada - saida

            devolver_conexao(conn)
            return t(f"💰 Entradas: R$ {entrada:.2f} | Saídas: R$ {saida:.2f} | Saldo: R$ {saldo:.2f}")
        except:
            devolver_conexao(conn)
            return t("Não foi possível acessar os dados financeiros.")

    # ===== VEÍCULOS =====
    if "veiculo" in pergunta_lower or "veículos" in pergunta_lower:
        try:
            cursor.execute("SELECT COUNT(*) FROM veiculos")
            total = cursor.fetchone()[0]

            devolver_conexao(conn)
            return t(f"🚗 Você possui {total} veículos cadastrados no sistema.")
        except:
            devolver_conexao(conn)
            return t("Não foi possível acessar os dados de veículos.")

    # ===== RELATÓRIOS =====
    if "relatorio" in pergunta_lower or "relatório" in pergunta_lower:
        devolver_conexao(conn)
        return t("📊 Você pode gerar relatórios completos nas abas de relatórios do sistema.")

    # ===== EXPLICAÇÕES =====
    if "como funciona" in pergunta_lower:
        devolver_conexao(conn)
        return t("O sistema possui módulos de estoque, financeiro, veículos e relatórios. Você pode gerenciar tudo em tempo real.")

    # ===== FALLBACK INTELIGENTE =====
    devolver_conexao(conn)

    return t("🤖 Não entendi completamente, mas posso te ajudar com estoque, financeiro, veículos e relatórios. Tente perguntar de outra forma.")


# ================= ROTA =================
@ia_bp.route("/ia", methods=["GET", "POST"])
def ia():
    if "user" not in session:
        return redirect("/")

    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":
        pergunta = request.form.get("pergunta")

        resposta = resposta_inteligente(pergunta)

        session["chat"].append({"role": "user", "content": pergunta})
        session["chat"].append({"role": "assistant", "content": resposta})

    historico = ""
    for msg in session["chat"]:
        if msg["role"] == "user":
            historico += f"<div class='msg user'>{msg['content']}</div>"
        else:
            historico += f"<div class='msg bot'>{msg['content']}</div>"

    return f"""
    <style>
        body {{ background:#0f0f0f; font-family: Arial; color:white; }}
        .container {{ width:90%; max-width:800px; margin:auto; margin-top:40px; }}
        .msg {{ padding:12px; border-radius:10px; margin:10px 0; max-width:70%; }}
        .user {{ background:#2b2b2b; margin-left:auto; }}
        .bot {{ background:#1a1a1a; margin-right:auto; }}
        .input-box {{ display:flex; margin-top:20px; }}
        input {{ flex:1; padding:15px; border-radius:10px; border:none; background:#2b2b2b; color:white; }}
        button {{ padding:15px; margin-left:10px; border:none; border-radius:10px; background:white; cursor:pointer; }}
    </style>

    <div class="container">
        <h2>💬 {t("IA KBSISTEMAS")}</h2>
        {historico}
        <form method="post" class="input-box">
            <input name="pergunta" placeholder="{t("Pergunte qualquer coisa...")}">
            <button>{t("Enviar")}</button>
        </form>
    </div>
    """
