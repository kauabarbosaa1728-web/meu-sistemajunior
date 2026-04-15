from flask import Blueprint, request, session, redirect
from banco import conectar, devolver_conexao
import difflib

ia_bp = Blueprint("ia_bp", __name__)

# ================= BUSCAR PRODUTO INTELIGENTE =================
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

# ================= IA INTELIGENTE =================
def resposta_inteligente(pergunta):
    pergunta_lower = pergunta.lower()

    conn = conectar()
    cursor = conn.cursor()

    # ===== TOTAL =====
    if any(p in pergunta_lower for p in ["quantos", "total", "temos", "existem"]):
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM estoque")
        qtd = cursor.fetchone()[0]

        devolver_conexao(conn)
        return f"📦 Atualmente você tem {total} produtos cadastrados, somando {qtd} itens no estoque."

    # ===== BUSCAR PRODUTO INTELIGENTE =====
    produto = encontrar_produto(pergunta)

    if produto:
        cursor.execute(
            "SELECT produto, quantidade FROM estoque WHERE LOWER(produto)=%s",
            (produto,)
        )
        resultado = cursor.fetchone()

        devolver_conexao(conn)

        if resultado:
            return f"📦 O produto '{resultado[0]}' possui {resultado[1]} unidades no estoque."

    # ===== LISTAR =====
    if any(p in pergunta_lower for p in ["listar", "mostrar", "ver", "estoque", "produtos"]):
        cursor.execute("SELECT produto, quantidade FROM estoque LIMIT 10")
        dados = cursor.fetchall()

        devolver_conexao(conn)

        if not dados:
            return "📭 Seu estoque está vazio."

        texto = "📋 Aqui estão alguns produtos:\n"
        for p, q in dados:
            texto += f"- {p}: {q}\n"

        return texto

    # ===== MAIOR =====
    if any(p in pergunta_lower for p in ["mais", "maior", "top"]):
        cursor.execute("SELECT produto, quantidade FROM estoque ORDER BY quantidade DESC LIMIT 1")
        p = cursor.fetchone()

        devolver_conexao(conn)

        if p:
            return f"🏆 O produto com maior quantidade é '{p[0]}' com {p[1]} unidades."

    # ===== SAUDAÇÃO =====
    if any(p in pergunta_lower for p in ["oi", "ola", "eai", "fala"]):
        devolver_conexao(conn)
        return "👋 Fala! Pode perguntar qualquer coisa sobre o sistema."

    devolver_conexao(conn)

    return "🤖 Não entendi muito bem, mas posso te ajudar com estoque, produtos e quantidades."

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
        <h2>💬 IA KBSISTEMAS</h2>
        {historico}
        <form method="post" class="input-box">
            <input name="pergunta" placeholder="Pergunte qualquer coisa...">
            <button>Enviar</button>
        </form>
    </div>
    """
