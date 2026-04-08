from flask import Blueprint, request, session, redirect
from openai import OpenAI
from banco import conectar, devolver_conexao
import os

ia_bp = Blueprint("ia_bp", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================= CONTEXTO DO SISTEMA =================
def contexto_sistema():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM estoque")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM estoque")
    total_qtd = cursor.fetchone()[0]

    devolver_conexao(conn)

    return f"""
    Você é uma IA do sistema KBSISTEMAS.
    Responda de forma simples, amigável e direta.

    Dados atuais:
    - Total de produtos: {total_produtos}
    - Quantidade total: {total_qtd}

    Se perguntarem algo do sistema, use esses dados.
    """

# ================= FALLBACK INTELIGENTE =================
def resposta_local(pergunta):
    pergunta = pergunta.lower()

    if "oi" in pergunta or "ola" in pergunta:
        return "👋 Fala! Como posso te ajudar no sistema?"

    if "tudo bem" in pergunta:
        return "Tudo certo 😎 e com você?"

    if "quantos produtos" in pergunta:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total = cursor.fetchone()[0]
        devolver_conexao(conn)
        return f"📦 Você tem {total} produtos cadastrados."

    return "🤖 Tenta perguntar sobre estoque ou algo do sistema 😉"


# ================= IA =================
@ia_bp.route("/ia", methods=["GET", "POST"])
def ia():
    if "user" not in session:
        return redirect("/")

    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":
        pergunta = request.form.get("pergunta")

        try:
            mensagens = [
                {"role": "system", "content": contexto_sistema()}
            ] + session["chat"] + [
                {"role": "user", "content": pergunta}
            ]

            resposta_openai = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=mensagens
            )

            resposta = resposta_openai.choices[0].message.content

        except Exception:
            resposta = resposta_local(pergunta)

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
        <h2>💬 IA KBSISTEMAS</h2>

        {historico}

        <form method="post" class="input-box">
            <input name="pergunta" placeholder="Pergunte qualquer coisa...">
            <button>Enviar</button>
        </form>
    </div>
    """
