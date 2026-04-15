from flask import Blueprint, request, session, redirect
from banco import conectar, devolver_conexao

ia_bp = Blueprint("ia_bp", __name__)

# ================= IA LOCAL (GRÁTIS) =================
def resposta_inteligente(pergunta):
    pergunta = pergunta.lower()

    conn = conectar()
    cursor = conn.cursor()

    # ===== TOTAL DE PRODUTOS =====
    if any(p in pergunta for p in ["quantos", "total"]) and any(p in pergunta for p in ["produto", "material", "item"]):
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM estoque")
        qtd = cursor.fetchone()[0]

        devolver_conexao(conn)
        return f"📦 Você tem {total} produtos cadastrados com {qtd} itens no total."

    # ===== PRODUTO ESPECÍFICO =====
    if "tem" in pergunta or "quantidade" in pergunta:
        palavras = pergunta.split()

        for palavra in palavras:
            cursor.execute(
                "SELECT produto, quantidade FROM estoque WHERE LOWER(produto) LIKE %s LIMIT 1",
                (f"%{palavra}%",)
            )
            resultado = cursor.fetchone()

            if resultado:
                devolver_conexao(conn)
                return f"📦 O produto '{resultado[0]}' tem {resultado[1]} unidades."

    # ===== LISTAR ESTOQUE =====
    if any(p in pergunta for p in ["listar", "mostrar", "estoque"]):
        cursor.execute("SELECT produto, quantidade FROM estoque LIMIT 10")
        dados = cursor.fetchall()

        if not dados:
            devolver_conexao(conn)
            return "📭 Seu estoque está vazio."

        texto = "📋 Estoque:\n"
        for p, q in dados:
            texto += f"- {p}: {q}\n"

        devolver_conexao(conn)
        return texto

    # ===== MAIOR ESTOQUE =====
    if any(p in pergunta for p in ["maior", "mais"]):
        cursor.execute("SELECT produto, quantidade FROM estoque ORDER BY quantidade DESC LIMIT 1")
        p = cursor.fetchone()

        devolver_conexao(conn)
        if p:
            return f"🏆 Produto com maior estoque: {p[0]} ({p[1]} unidades)"

    # ===== SAUDAÇÃO =====
    if any(p in pergunta for p in ["oi", "ola", "eai"]):
        devolver_conexao(conn)
        return "👋 Fala! Pergunta algo sobre o estoque 😉"

    devolver_conexao(conn)
    return "🤖 Não entendi. Tente perguntar sobre estoque."

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
        body {{
            background:#0f0f0f;
            font-family: Arial;
            color:white;
        }}

        .container {{
            width:90%;
            max-width:800px;
            margin:auto;
            margin-top:40px;
        }}

        .msg {{
            padding:12px;
            border-radius:10px;
            margin:10px 0;
            max-width:70%;
        }}

        .user {{
            background:#2b2b2b;
            margin-left:auto;
        }}

        .bot {{
            background:#1a1a1a;
            margin-right:auto;
        }}

        .input-box {{
            display:flex;
            margin-top:20px;
        }}

        input {{
            flex:1;
            padding:15px;
            border-radius:10px;
            border:none;
            background:#2b2b2b;
            color:white;
        }}

        button {{
            padding:15px;
            margin-left:10px;
            border:none;
            border-radius:10px;
            background:white;
            cursor:pointer;
        }}
    </style>

    <div class="container">
        <h2>💬 IA KBSISTEMAS (GRÁTIS)</h2>

        {historico}

        <form method="post" class="input-box">
            <input name="pergunta" placeholder="Pergunte sobre o sistema...">
            <button>Enviar</button>
        </form>
    </div>
    """
