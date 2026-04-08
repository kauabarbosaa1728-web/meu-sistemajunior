from flask import Blueprint, request, session, redirect
from openai import OpenAI
from banco import conectar, devolver_conexao
import os

# ================= BLUEPRINT =================
ia_bp = Blueprint("ia_bp", __name__)

# ================= OPENAI =================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================= FUNÇÃO FALLBACK (GRÁTIS) =================
def resposta_local(pergunta):
    conn = conectar()
    cursor = conn.cursor()

    pergunta = pergunta.lower()

    if "quantos produtos" in pergunta:
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total = cursor.fetchone()[0]
        devolver_conexao(conn)
        return f"📦 Você tem {total} produtos cadastrados."

    elif "quantidade total" in pergunta:
        cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM estoque")
        total = cursor.fetchone()[0]
        devolver_conexao(conn)
        return f"📊 Quantidade total no estoque: {total}"

    elif "listar produtos" in pergunta:
        cursor.execute("SELECT produto FROM estoque LIMIT 10")
        produtos = [p[0] for p in cursor.fetchall()]
        devolver_conexao(conn)
        return "📝 Produtos: " + ", ".join(produtos)

    devolver_conexao(conn)
    return "🤖 IA gratuita: não entendi, tente perguntar sobre estoque."


# ================= IA CHAT =================
@ia_bp.route("/ia", methods=["GET", "POST"])
def ia():
    if "user" not in session:
        return redirect("/")

    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":
        pergunta = request.form.get("pergunta")

        try:
            resposta_openai = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=session["chat"] + [
                    {"role": "user", "content": pergunta}
                ]
            )

            resposta = resposta_openai.choices[0].message.content

        except Exception as e:
            # 🔥 FALLBACK AUTOMÁTICO
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
